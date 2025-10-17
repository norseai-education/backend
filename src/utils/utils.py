import asyncio
import threading
import json
import re

from src.utils import logging
from src.utils.text_to_vec import TextToVec
from src.services.problem_service import ProblemHandler

# Configure logging
logger = logging.set_logger(__name__)

def parse_problem(response):
    problem_handler = ProblemHandler()
    
    # Use regex to check if response contains {'problem_id':<id>} pattern
    if "problem_id" in response:
        pattern = r"\{'problem_id':\s*'([^']+)'\}"
        match = re.search(pattern, response)
        
        if match:
            problem_id = match.group(1).strip()
            logging.log(f"Problem ID found: {problem_id}", logger, 2)
            problem = problem_handler.get_problem(problem_id)
            
            if problem:
                # Replace the problem_id pattern with the actual problem content
                problem_text = str(problem)  # Convert problem to string
                modified_response = re.sub(pattern, problem_text, response)
                return modified_response
            else:
                logging.log(f"Problem not found for ID: {problem_id}", logger, 2)
                return response
        else:
            logging.log("Couldn't extract ID from response", logger, 2)
            return response
    else:
        logging.log("No problem ID found in response", logger, 2)
        return response



def transfer_to_chroma():
    text_to_vec = TextToVec()
    text_to_vec.math_related_to_vec()
    text_to_vec.student_persona_to_vec()
    text_to_vec.conversation_history_to_vec()

def convert_messages_to_dict(messages, student_id):
    """
    Converts a list of HumanMessage and AIMessage objects to a list of dictionaries.
    
    Args:
        messages: List containing HumanMessage and AIMessage objects
        
    Returns:
        List of dictionaries with 'student'/'teacher' keys and content values
    """
    result = []
    
    for message in messages:
        # Get the class name to determine message type
        message_type = message.__class__.__name__
        
        if message_type == 'HumanMessage':
            result.append({'student_id': str(student_id), 'role': 'student', 'content': message.content})
        elif message_type == 'AIMessage':
            result.append({'student_id': str(student_id), 'role': 'teacher', 'content': message.content})
    
    return result

def store_input(database, collection_name, student_id, student_input):
    """Store student input in background without blocking the main flow"""
    logging.log("Storing student input to student_persona collection...", logger, 2)
    def background_task():
        try:
            # Try to use existing event loop if available
            loop = asyncio.get_running_loop()
            asyncio.create_task(
                database.insert_document(collection_name, {"student_id": str(student_id), "content": student_input})
            )
        except RuntimeError:
            # No event loop running, create a new one
            asyncio.run(
                database.insert_document(collection_name, {"student_id": str(student_id), "content": student_input})
            )
        except Exception as e:
            logging.log(f"Background storage error: {e}", logger, 0)  # Log but don't crash
    
    # Run in daemon thread so it doesn't block program exit
    thread = threading.Thread(target=background_task)
    thread.daemon = True
    thread.start()

def check_lesson_state(lesson_state):
    if not isinstance(lesson_state, dict):
        try:
            lesson_state = json.loads(lesson_state)
        except json.JSONDecodeError:
            return False
    # Count 'in progress' values and track their indices
    in_progress_count = 0
    in_progress_indices = []
    
    for key, value in lesson_state.items():
        if key not in ['START_LESSON','GIVE_PROBLEM', 'PROBLEM_WALKTHROUGH', 'END_LESSON', 'CHECK', 'BEHIND']:
            return False
        if value.lower() not in ['done', 'in progress', 'not done']:
            return False
        
        # Track 'in progress' values and their indices
        if value.lower() == 'in progress':
            in_progress_count += 1
            in_progress_indices.append(list(lesson_state.keys()).index(key))
    
    # If there are 2 'in progress' values, turn the one with smallest index to 'done'
    if in_progress_count == 2:
        logging.log('Two In Progress found in lesson state, fixing now...', logger, 2)
        smallest_index = min(in_progress_indices)
        key_at_smallest_index = list(lesson_state.keys())[smallest_index]
        lesson_state[key_at_smallest_index] = 'Done'
    return lesson_state

def parse_response(text):
    problem_handler = ProblemHandler()
    default_response = "I'm sorry, can you repeat that?"
    default_lesson_state = {
        'START_LESSON': 'Done',
        'GIVE_PROBLEM': 'Not Done',
        'PROBLEM_WALKTHROUGH': 'Not Done',
        'GIVE_PROBLEM': 'Not Done',
        'END_LESSON': 'Not Done'
    }
    
    # Find the Final Answer section     
    teaching_response = ""
    lesson_state = {}
    
    try:
        # Try to parse as JSON first
        parsed_data = json.loads(text)
        if isinstance(parsed_data, dict):
            logging.log("Parsed response as json!", logger, 2)
            teaching_response = parsed_data.get("teacher_response", "")
            lesson_state = parsed_data.get("lesson_state", {})
            problem_id = parsed_data.get("problem_id", "")
            logging.log(f"\nExtracted teacher_response: {teaching_response}\nExtracted lesson_match: {lesson_state}\nExtracted problem_id_match: {problem_id}\n", logger, 2)
            
            problem = problem_handler.get_problem(problem_id)
            if not problem:
                logging.log(f"Problem not found for ID: {problem_id}", logger, 2)
                problem = ""
                
            teaching_response = str(teaching_response) + str(problem)
            logging.log(f"Teaching response with problem: {teaching_response}", logger, 2)

    except json.JSONDecodeError:
        # Fallback: Try to extract from structured text format
        teaching_match = re.search(r'teacher_response:\s*(.*?)(?=lesson_state:|$)', text, re.DOTALL)
        lesson_match = re.search(r'lesson_state:\s*(\{.*\})', text, re.DOTALL)
        problem_id_match = re.search(r'problem_id:\s*"([^"]+)"', text, re.DOTALL)
        logging.log(f"Found regex match!\nExtracted teacher_response: {teaching_match}\nExtracted lesson_match: {lesson_match}\nExtracted problem_id_match: {problem_id_match}\n", logger, 2)
        if problem_id_match:
            problem_id = problem_id_match.group(1).strip()  
            
            if not problem:
                logging.log(f"Problem not found for ID: {problem_id}", logger, 2)
                problem = ""

        if teaching_match:
            teaching_response = teaching_match.group(1).strip()
            teaching_response = str(teaching_response) + str(problem)
            logging.log(f"Teaching response with problem: {teaching_response}", logger, 2)


        if lesson_match:
            try:
                lesson_state = json.loads(lesson_match.group(1))
            except json.JSONDecodeError:
                logging.log("Failed to parse lesson state JSON", logger, 0)
                lesson_state = {}
    
    lesson_state = check_lesson_state(lesson_state)
    # Error handling logic
    if lesson_state:  # state_dict exists
        if teaching_response:
            return lesson_state, teaching_response
        else:
            logging.log("Teacher response not found, using default", logger, 2)
            return lesson_state, default_response
    else:
        # return default lesson state
        logging.log("Lesson state not found, using default", logger, 2)
        return default_lesson_state, default_response
    

def format_conversation_context(messages):
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
    logging.log(f"Context formatted: {formatted_context}", logger, 2)
    return formatted_context

def get_learning_obj(graph):
    for key,value in graph.items():
        if value < 0.75:
            return key
    return None