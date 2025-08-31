from langchain.agents import create_react_agent, AgentExecutor
from state import State
import re
import asyncio
import json
import threading
import utils

# Configure logging
logger = utils.set_logger(__name__)

class MathTeacher:
    def __init__(self, model, prompt, store, list_of_tools):
        self.model = model
        self.prompt = prompt
        self.store=store
        self.store.connect("amc8_database")
        self.tools = list_of_tools

    def store_input(self, student_id, input):
        """Store student input in background without blocking the main flow"""
        utils.log("Storing teacher response to math_related collection...", logger, 2)
        def background_task():
            try:
                # Try to use existing event loop if available
                loop = asyncio.get_running_loop()
                asyncio.create_task(
                    self.store.insert_document('math_related', {"student_id": str(student_id), "content": input})
                )
            except RuntimeError:
                # No event loop running, create a new one
                asyncio.run(
                    self.store.insert_document('math_related', {"student_id": str(student_id), "content": input})
                )
            except Exception as e:
                utils.log(f"Background storage error: {e}", logger, 0)  # Log but don't crash
        
        # Run in daemon thread so it doesn't block program exit
        thread = threading.Thread(target=background_task)
        thread.daemon = True
        thread.start()

    def check_lesson_state(self, lesson_state):
        if not isinstance(lesson_state, dict):
            try:
                lesson_state = json.loads(lesson_state)
            except json.JSONDecodeError:
                return False
        # Count 'in progress' values and track their indices
        in_progress_count = 0
        in_progress_indices = []
        
        for key, value in lesson_state.items():
            if key not in ['START_LESSON','CONCEPT_INTRODUCTION','GIVE_EASIER_PROBLEM', 'PROBLEM_WALKTHROUGH', 'GIVE_HARDER_PROBLEM', 'END_LESSON', 'CHECK']:
                return False
            if value.lower() not in ['done', 'in progress', 'not done']:
                return False
            
            # Track 'in progress' values and their indices
            if value.lower() == 'in progress':
                in_progress_count += 1
                in_progress_indices.append(list(lesson_state.keys()).index(key))
        
        # If there are 2 'in progress' values, turn the one with smallest index to 'done'
        if in_progress_count == 2:
            utils.log('Two In Progress found in lesson state, fixing now...', logger, 2)
            smallest_index = min(in_progress_indices)
            key_at_smallest_index = list(lesson_state.keys())[smallest_index]
            lesson_state[key_at_smallest_index] = 'Done'
        return lesson_state

    def parse_response(self, text):
        default_response = "I'm sorry, can you repeat that?"
        default_lesson_state = {
            'START_LESSON': 'Done',
            'CONCEPT_INTRODUCTION': 'In Progress', 
            'GIVE_EASIER_PROBLEM': 'Not Done',
            'PROBLEM_WALKTHROUGH': 'Not Done',
            'GIVE_HARDER_PROBLEM': 'Not Done',
            'END_LESSON': 'Not Done'
        }
        
        # Find the Final Answer section     
        teaching_response = ""
        lesson_state = {}
        
        try:
            # Try to parse as JSON first
            parsed_data = json.loads(text)
            if isinstance(parsed_data, dict):
                utils.log("Parsed response as json!", logger, 2)
                teaching_response = parsed_data.get("teacher_response", "")
                lesson_state = parsed_data.get("lesson_state", {})
                utils.log(f"\nExtracted teacher_response: {teaching_response}\nExtracted lesson_match: {lesson_state}\n", logger, 2)
                
        except json.JSONDecodeError:
            # Fallback: Try to extract from structured text format
            teaching_match = re.search(r'teacher_response:\s*(.*?)(?=lesson_state:|$)', text, re.DOTALL)
            lesson_match = re.search(r'lesson_state:\s*(\{.*\})', text, re.DOTALL)
            utils.log(f"Found regex match!\nExtracted teacher_response: {teaching_match}\nExtracted lesson_match: {lesson_match}\n", logger, 2)
            
            if teaching_match:
                teaching_response = teaching_match.group(1).strip()
            
            if lesson_match:
                try:
                    lesson_state = json.loads(lesson_match.group(1))
                except json.JSONDecodeError:
                    utils.log("Failed to parse lesson state JSON", logger, 0)
                    lesson_state = {}
        
        lesson_state = self.check_lesson_state(lesson_state)
        # Error handling logic
        if lesson_state:  # state_dict exists
            if teaching_response:
                return lesson_state, teaching_response
            else:
                utils.log("Teacher response not found, using default", logger, 2)
                return lesson_state, default_response
        else:
            # return default lesson state
            utils.log("Lesson state not found, using default", logger, 2)
            return default_lesson_state, default_response

    def format_conversation_context(self, messages):
        """Format conversation messages with speaker labels"""
        formatted_context = []
        for msg in messages:
            if hasattr(msg, 'content'):  # For HumanMessage/AIMessage objects
                if hasattr(msg, '__class__') and 'Human' in msg.__class__.__name__:
                    formatted_context.append(f"Student: {msg.content}")
                elif hasattr(msg, '__class__') and 'AI' in msg.__class__.__name__:
                    formatted_context.append(f"Teacher: {msg.content}")
                else:
                    formatted_context.append(f"Unknown: {msg.content}")
            elif isinstance(msg, dict) and 'role' in msg:  # For dict format
                if msg['role'] == 'human':
                    formatted_context.append(f"Student: {msg['content']}")
                elif msg['role'] == 'assistant':
                    formatted_context.append(f"Teacher: {msg['content']}")
                else:
                    formatted_context.append(f"{msg['role'].title()}: {msg['content']}")
            else:
                formatted_context.append(f"Unknown: {str(msg)}")
        utils.log(f"Context formatted: {formatted_context}", logger, 2)
        return formatted_context

    def build_node(self, state: State):
        utils.log(f"Current state: \n{state}", logger, 2)
        utils.log(f"Going through math teacher node...", logger, 2)
        student_input = state["messages"][-1]
        learning_objective = state.get("cur_learning_objective", "DEFAULT")
        solution = state.get("solution", "DEFAULT")
        math_context = state.get("math_context", "DEFAULT")
        student_id = state.get("student_id", "default_student")
        lesson_state = state.get("lesson_state")
        learning_status = state.get("learning_status")
        context = self.format_conversation_context(state["messages"])
        cur_mastery = state.get("cur_mastery")

        teacher_prompt = self.prompt.get_prompt(lesson_state, learning_status)
        

        agent = create_react_agent(
            llm=self.model,
            tools=self.tools,
            prompt=teacher_prompt
        )

        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=5
        )

        utils.log("Getting math teacher response...", logger, 2)

        response = agent_executor.invoke({                                            # Inputs: student_input, learning_objective, solution, math_context | Outputs: response
            "student_input": student_input,
            "student_id": student_id,
            "learning_objective": learning_objective,
            "solution": solution,
            "math_context": math_context,
            "context": context,
            "lesson_state": lesson_state,
            "cur_mastery": cur_mastery
            }
        )

    
        raw_response = response["output"]

        utils.log(f"Raw response: \n{raw_response}\n type: {type(raw_response)}", logger, 2)

        new_lesson_state, final_response = self.parse_response(response["output"])
        
        # add teacher response to math-related-db
        self.store_input(student_id, final_response)

        return {"messages": [{"role": "assistant", "content": final_response}],
                "lesson_state": new_lesson_state
                }

    
