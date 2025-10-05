import asyncio
import json
from typing import Dict, Any, AsyncGenerator
from fastapi import HTTPException

from backend.src.services.graph import BuildNorseAIGraph
from backend.src.services.state_manager import StateManager
from backend.src.services.MongoDBHandler import MongoDBHandler
from backend.src.services.assessment_service import AssessmentService
from backend.src.config.settings import settings
from backend.src.utils import logging
from backend.src.utils import utils
from backend.src.utils import knowledge_info


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
        
        # Load states
        persisted_state = await asyncio.get_event_loop().run_in_executor(
            None, state_manager.retrieve
        )
        redis_state = await asyncio.get_event_loop().run_in_executor(
            None, state_manager.get_redis_state
        )
        user_state = state_manager.default_state()
        
        logging.log(f"Mongo DB state: \n{persisted_state}\n", self.logger, 2)
        logging.log(f"Redis state : \n{redis_state}\n", self.logger, 2)
        
        if not user_graph:
            # Apply persisted state
            if persisted_state:
                logging.log("Applying persisted state from MongoDB...", self.logger, 1)
                for key, value in persisted_state.items():
                    if key in user_state:
                        user_state[key] = value
                user_state['init_learning_objective'] = user_state['cur_learning_objective']
                logging.log("State from MongoDB applied!", self.logger, 1)
            
            # Apply Redis state
            if redis_state:
                logging.log("Applying Redis state...", self.logger, 1)
                for key, value in redis_state.items():
                    if key in user_state:
                        user_state[key] = value
                logging.log("State from Redis applied!", self.logger, 1)
        else:
            user_state['bkt_graph'] = user_graph
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
                    utils.transfer_to_chroma()
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
                    logging.convert_messages_to_dict(user_state["messages"]),
                    True
                )
                
                yield f"data: {json.dumps({'type': 'lesson_complete', 'message': 'Lesson completed! State saved.'})}\n\n"
                await self.cleanup_session(student_id)
                return
            
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
            
            # Run the graph in executor to avoid blocking
            user_state = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: norseai.invoke(user_state, {"configurable": {"thread_id": str(student_id)}})
            )
            
            # Update session state
            session['user_state'] = user_state
            logging.log(f"State after: \n{user_state}", self.logger, 1)
            
            # Extract and send AI response
            if "messages" in user_state and user_state["messages"]:
                last_message = user_state["messages"][-1]
                if hasattr(last_message, 'type') and last_message.type == 'ai':
                    ai_response = last_message.content
                    yield f"data: {json.dumps({'type': 'ai_response', 'content': ai_response})}\n\n"
                elif hasattr(last_message, 'role') and last_message.get('role') == 'assistant':
                    ai_response = last_message.get('content', '')
                    yield f"data: {json.dumps({'type': 'ai_response', 'content': ai_response})}\n\n"
            
            # Send completion signal
            # yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            logging.log(f"Error processing message for student {student_id}: {str(e)}", self.logger, 2)
            yield f"data: {json.dumps({'type': 'error', 'message': f'An error occurred: {str(e)}'})}\n\n"
    
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

            # Only save conversation history if there are messages
            messages_dict = utils.convert_messages_to_dict(user_state["messages"], student_id)
            if messages_dict:
                await convo_db.insert_document(
                    "conversation_history",
                    messages_dict,
                    True
                )
                logging.log("Stored conversation history into database!", self.logger, 1)
            else:
                logging.log("No messages to store for this session", self.logger, 1)
            
            # Clear Redis memory
            await asyncio.get_event_loop().run_in_executor(None, state_manager.clear_redis_memory)
            await self.cleanup_session(student_id)
            
            return f"Session ended for student {student_id}"
        else:
            raise HTTPException(status_code=404, detail="Session not found")

# Global instance
chat_service = ChatService()