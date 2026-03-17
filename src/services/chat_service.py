import asyncio
import json
import base64
from typing import Dict, Any, AsyncGenerator
from fastapi import HTTPException
import traceback
from src.services.graph import BuildNorseAIGraph
from src.services.state_manager import StateManager
from src.services.MongoDBHandler import MongoDBHandler
from src.services.assessment_service import AssessmentService
from src.config.settings import settings
from langchain_core.messages import HumanMessage
from src.utils import logging
from src.utils import utils
from src.utils import knowledge_info
from src.services.tts_service import stream_tts_audio


class ChatService:
    def __init__(self):
        self.assessment_service = AssessmentService()
        self.active_sessions: Dict[int, Dict[str, Any]] = {}
        self.logger = logging.set_logger(__name__)
    
    async def initialize_session(self, student_id: int, user_graph: dict = None) -> Dict[str, Any]:
        """Initialize or retrieve student session with all components"""
        
        logging.log(f"Initializing new session for student {student_id}", self.logger, 1)
        logging.log(f"User graph: {user_graph}", self.logger, 1)
        
        # Initialize graph
        state_manager = StateManager(student_id)
        graph = BuildNorseAIGraph()
        graph_builder = graph.get_graph()
        norseai = state_manager.build_graph_redis(graph_builder)
        
        # Initialize MongoDB connection
        convo_db = MongoDBHandler(settings.mongodb_url)
        await asyncio.get_event_loop().run_in_executor(
            None, convo_db.connect, settings.mongodb_database
        )

        user_state = state_manager.default_state()
        
        if not user_graph:  
                # Load states
            persisted_state = await asyncio.get_event_loop().run_in_executor(
                None, state_manager.retrieve
            )
            redis_state = await asyncio.get_event_loop().run_in_executor(
                None, state_manager.get_redis_state
            )

            
            logging.log(f"Mongo DB state: \n{persisted_state}\n", self.logger, 2)
            logging.log(f"Redis state : \n{redis_state}\n", self.logger, 2)
            # Apply persisted state
            if persisted_state:
                logging.log("State found from MongoDB! Applying...", self.logger, 1)
                for key, value in persisted_state.items():
                    if key in user_state:
                        user_state[key] = value
                user_state['init_learning_objective'] = user_state['cur_learning_objective']
                user_state['cur_mastery'] = [knowledge_info.amc8_concepts[:knowledge_info.amc8_concepts.index(user_state["cur_learning_objective"])]]
                logging.log("State from MongoDB applied!", self.logger, 1)
            
            # Apply Redis state
            if redis_state:
                logging.log("Redis state foud! Applying Redis state...", self.logger, 1)
                for key, value in redis_state.items():
                    if key in user_state:
                        user_state[key] = value
                logging.log("State from Redis applied!", self.logger, 1)
        else:
            user_state['bkt_graph'] = user_graph
            user_state["init_learning_objective"] = utils.get_learning_obj(user_graph)
            user_state["cur_learning_objective"] = user_state["init_learning_objective"]
            user_state['cur_mastery'] = [knowledge_info.amc8_concepts[:knowledge_info.amc8_concepts.index(user_state["cur_learning_objective"])]]
            logging.log("User graph from assessment applied!", self.logger, 1)
        
        # Store session
        session_data = {
            'state_manager': state_manager,
            'norseai': norseai,
            'convo_db': convo_db,
            'user_state': user_state
        }
        logging.log(f"Session data: {session_data}", self.logger, 2)
        
        self.active_sessions[student_id] = session_data
        return session_data
    
    async def get_session(self, student_id: int) -> Dict[str, Any]:
        """Get existing session or create new one"""
        logging.log(f"Active sessions: {self.active_sessions}", self.logger, 2)
        
        if student_id not in self.active_sessions:
            await self.initialize_session(student_id)
        
        return self.active_sessions[student_id]
    
    async def cleanup_session(self, student_id: int):
        """Clean up session resources"""
        if student_id in self.active_sessions:
            session = self.active_sessions[student_id]
            try:
                # Close database connection
                if 'convo_db' in session:
                    await utils.transfer_to_chroma()
                    session['convo_db'].close()
                logging.log(f"Session cleanup completed for student {student_id}", self.logger, 1)
            except Exception as e:
                logging.log(f"Error during session cleanup for student {student_id}: {e}", self.logger, 1)
            finally:
                # Remove from active sessions
                del self.active_sessions[student_id]
    
    async def cleanup_all_sessions(self):
        """Clean up all active sessions"""
        for student_id in list(self.active_sessions.keys()):
            await self.cleanup_session(student_id)
    
    async def get_chat_response(self, student_id: int, message: str) -> AsyncGenerator[str, None]:
        """Get streaming chat response"""
        try:
            session = await self.get_session(student_id)
            state_manager = session['state_manager']
            norseai = session['norseai']
            convo_db = session['convo_db']
            user_state = session['user_state']
            
            # Manage conversation history length
            if len(user_state['messages']) > settings.max_conversation_length:
                old_messages = user_state["messages"][:-settings.conversation_keep_recent]
                asyncio.create_task(
                    convo_db.insert_document(
                        'conversation_history', 
                        utils.convert_messages_to_dict(old_messages, student_id),
                        True
                    )
                )
                user_state["messages"] = user_state["messages"][-settings.conversation_keep_recent:]
                logging.log(f"Trimmed conversation history for student {student_id}", self.logger, 1)
            
            # Check if lesson is complete
            if user_state.get("lesson_state", {}).get("END_LESSON", "").lower() == "done":
                # Store final state
                await asyncio.get_event_loop().run_in_executor(None, state_manager.store, user_state)
                await asyncio.get_event_loop().run_in_executor(None, state_manager.clear_redis_memory)
                
                # Store final conversation
                await convo_db.insert_document(
                    "conversation_history",
                    utils.convert_messages_to_dict(user_state["messages"], student_id),
                    True
                )
                
                yield f"data: {json.dumps({'type': 'lesson_complete', 'message': 'Lesson completed! State saved.'})}\n\n"
                await self.cleanup_session(student_id)
                return
            
            user_state["messages"] = utils.convert_redis_messages(user_state["messages"])
            # Add user message to state
            user_state["messages"] = user_state.get("messages", []) + [
                {"role": "user", "content": message}
            ]

            
            
            # Send user message
            # yield f"data: {json.dumps({'type': 'user_message', 'content': message})}\n\n"
            
            # Get response
            # yield f"data: {json.dumps({'type': 'thinking', 'message': 'Processing...'})}\n\n"
            
            logging.log("Running the graph now...", self.logger, 1)
            logging.log(f"State before: \n{user_state}", self.logger, 1)
            
            # Stream tokens using LangGraph's built-in streaming with ChatOllama
            buffer = ""
            last_extracted_length = 0
            tts_token_queue = asyncio.Queue()
            tts_audio_queue = asyncio.Queue()
            tts_done = False
            
            async def token_generator():
                """Async generator that yields tokens from queue for TTS"""
                while True:
                    token = await tts_token_queue.get()
                    if token is None:  # Sentinel value
                        break
                    yield token
            
            async def tts_processor():
                """Process TTS streaming in background and put audio in queue"""
                try:
                    async for audio_data in stream_tts_audio(token_generator()):
                        await tts_audio_queue.put(audio_data)
                    await tts_audio_queue.put(None)  # Signal completion
                except Exception as e:
                    logging.log(f"TTS processor error: {e}", self.logger, 1)
                    await tts_audio_queue.put(None)
            
            # Start TTS processor task
            tts_task = None
            
            for message_chunk, metadata in norseai.stream(
                user_state,
                stream_mode="messages",
                config={"configurable": {"thread_id": str(student_id)}}
            ):
                if metadata["langgraph_node"] == "teacher" or metadata["langgraph_node"] == "math_teacher":
                    buffer += message_chunk.content
                    # logging.log(f"Buffer: {buffer}", self.logger, 2)
                    
                    # Extract incremental value from buffer
                    value, used_length = utils.extract_json_value(buffer, "teacher_response")
                    
                    # Get only the new tokens since last extraction
                    if value and len(value) > last_extracted_length:
                        new_tokens = value[last_extracted_length:]
                        logging.log(f"New LLM tokens: {new_tokens}", self.logger, 1)
                        
                        # Initialize TTS connection on first token
                        if tts_task is None and new_tokens.strip():
                            # Put first token in queue BEFORE starting task to ensure it's available
                            # when stream_tts_audio waits for the first token
                            await tts_token_queue.put(new_tokens)
                            # Now start TTS processor - it will find the token ready
                            tts_task = asyncio.create_task(tts_processor())
                            last_extracted_length = len(value)
                        else:
                            # Send subsequent tokens to TTS queue immediately
                            if new_tokens.strip():
                                await tts_token_queue.put(new_tokens)
                                last_extracted_length = len(value)
                        
                        # Stream any available audio chunks while processing (non-blocking)
                        try:
                            while True:
                                audio_data = tts_audio_queue.get_nowait()
                                if audio_data is None:
                                    tts_done = True
                                    break
                                
                                # Encode and yield audio chunk
                                if isinstance(audio_data, bytes):
                                    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                                    yield f"data: {json.dumps({'type': 'audio_stream', 'audio_chunk': audio_b64})}\n\n"
                                elif isinstance(audio_data, str):
                                    try:
                                        meta = json.loads(audio_data)
                                        yield f"data: {json.dumps({'type': 'audio_metadata', **meta})}\n\n"
                                    except:
                                        pass
                        except asyncio.QueueEmpty:
                            pass  # No audio ready yet, continue
            
            # Signal end of tokens to TTS
            await tts_token_queue.put(None)
            
            # Collect remaining audio chunks
            if tts_task:
                while not tts_done:
                    try:
                        audio_data = await asyncio.wait_for(tts_audio_queue.get(), timeout=0.1)
                        if audio_data is None:
                            break
                        
                        if isinstance(audio_data, bytes):
                            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                            yield f"data: {json.dumps({'type': 'audio_stream', 'audio_chunk': audio_b64})}\n\n"
                        elif isinstance(audio_data, str):
                            try:
                                meta = json.loads(audio_data)
                                yield f"data: {json.dumps({'type': 'audio_metadata', **meta})}\n\n"
                            except:
                                pass
                    except asyncio.TimeoutError:
                        # Check if task is done
                        if tts_task.done():
                            break
                
                # Wait for TTS task to complete
                try:
                    await tts_task
                except Exception as e:
                    logging.log(f"TTS task error: {e}", self.logger, 1)

            # grab final graph state
            logging.log("Grabbing final graph state...", self.logger, 1)
            user_state = state_manager.get_redis_state()
            # logging.log(f"Retrieved state from redis: \n{user_state}", self.logger, 1)

            user_state["messages"] = utils.convert_redis_messages(user_state["messages"])
            
            # Update session state
            session['user_state'] = user_state
            logging.log(f"State after: \n{user_state}", self.logger, 1)
            
            # Extract and send AI response
            # if "messages" in user_state and user_state["messages"]:
            #     last_message = user_state["messages"][-1]
            #     if hasattr(last_message, 'type') and last_message.type == 'ai':
            #         ai_response = last_message.content
            #         yield f"data: {json.dumps({'type': 'ai_response', 'content': ai_response})}\n\n"
            #     elif hasattr(last_message, 'role') and last_message.get('role') == 'assistant':
            #         ai_response = last_message.get('content', '')
            #         yield f"data: {json.dumps({'type': 'ai_response', 'content': ai_response})}\n\n"
            
            last_message = user_state["display_response"]
            eval_response = user_state.get("evaluation", "")
            eval_grade = user_state.get("evaluator_grade", "")
            yield f"data: {json.dumps({'type': 'ai_response', 'content': last_message, 'evaluation': eval_response, 'grade': eval_grade})}\n\n"
            
        except Exception as e:
            err = f"Error processing message for student {student_id}: {repr(e)}"
            tb = traceback.format_exc()
            logging.log(err + "\n" + tb, self.logger, 1)
            yield f"data: {json.dumps({'type': 'error', 'message': f'{err}'})}\n\n"
    
    def get_session_status(self, student_id: int) -> Dict[str, Any]:
        """Get current student status"""
        if student_id in self.active_sessions:
            user_state = self.active_sessions[student_id]['user_state']
            return {
                "active": True,
                "message_count": len(user_state.get('messages', [])),
                "lesson_state": user_state.get('lesson_state', {}),
                "current_objective": user_state.get('cur_learning_objective', '')
            }
        else:
            return {"active": False}
    
    async def end_session(self, student_id: int) -> str:
        """Manually end chat session"""
        if student_id in self.active_sessions:
            session = self.active_sessions[student_id]
            state_manager = session['state_manager']
            convo_db = session['convo_db']
            user_state = session['user_state']

            await convo_db.insert_document(
                "conversation_history",
                utils.convert_messages_to_dict(user_state["messages"], student_id),
                True
            )
            logging.log("Stored conversation history into database!", self.logger, 1)
            logging.log(f"Sample insert: \n{utils.convert_messages_to_dict(user_state["messages"])[:3]}\n", self.logger, 1)
            
            # Store final state in mongoDB
            await asyncio.get_event_loop().run_in_executor(None, state_manager.store, user_state)
            # Clear Redis memory
            await asyncio.get_event_loop().run_in_executor(None, state_manager.clear_redis_memory)
            await self.cleanup_session(student_id)
            
            return f"Session ended for student {student_id}"
        else:
            raise HTTPException(status_code=404, detail="Session not found")

# Global instance
chat_service = ChatService()