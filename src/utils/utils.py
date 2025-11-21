import asyncio
import concurrent.futures
import threading
import json
import re

from src.utils import logging
from src.utils import knowledge_info
from src.utils.text_to_vec import TextToVec
from src.services.problem_service import ProblemHandler
from typing import List, Dict, Any

# LangChain message types/deserialization helpers

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, messages_from_dict 

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



async def transfer_to_chroma():
    """Transfer MongoDB documents to ChromaDB in parallel for all collections."""
    loop = asyncio.get_event_loop()
    
    def _transfer_sync():
        text_to_vec = TextToVec()
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(text_to_vec.math_related_to_vec),
                executor.submit(text_to_vec.student_persona_to_vec),
                executor.submit(text_to_vec.conversation_history_to_vec)
            ]
            concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)
            # Check for exceptions and propagate them
            for future in futures:
                future.result()  # Raises exception if one occurred
    
    await loop.run_in_executor(None, _transfer_sync)

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

    if "In Progress" not in lesson_state.values():
        # Find the latest "done" value and set the next one to "in progress"
        keys = list(lesson_state.keys())
        latest_done_index = -1
        
        # Find the index of the latest "done" value
        for i, (key, value) in enumerate(lesson_state.items()):
            if value.lower() == 'done':
                latest_done_index = i
        
        # If we found a "done" value and there's a next item, set it to "in progress"
        if latest_done_index >= 0 and latest_done_index + 1 < len(keys):
            next_key = keys[latest_done_index + 1]
            lesson_state[next_key] = "In Progress"
            logging.log(f'No "In Progress" found, setting {next_key} to "In Progress"', logger, 2)
            
    # Count 'in progress' values and track their indices
    in_progress_count = 0
    in_progress_indices = []
    check_done = 0
    
    for key, value in lesson_state.items():
        if key not in ['START_LESSON','GIVE_FIRST_PROBLEM', 'FIRST_PROBLEM_WALKTHROUGH', 'GIVE_SECOND_PROBLEM', 'SECOND_PROBLEM_WALKTHROUGH', 'GIVE_THIRD_PROBLEM', 'THIRD_PROBLEM_WALKTHROUGH', 'END_LESSON', "CHECK", "BEHIND"]:
            return False
        if value.lower() not in ['done', 'in progress', 'not done']:
            return False
        
        # Track 'in progress' values and their indices
        if value.lower() == 'in progress':
            check_done = 1
            in_progress_count += 1
            in_progress_indices.append(list(lesson_state.keys()).index(key))


        if check_done == 0:
            if value.lower() != 'done':
                lesson_state[key] = "Done"

    
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
    
    # Find the Final Answer section     
    teaching_response = ""
    context_response = ""
    solution = ""
    
    try:
        # Try to parse as JSON first
        parsed_data = json.loads(text)
        if isinstance(parsed_data, dict):
            logging.log("Parsed response as json!", logger, 2)
            teaching_response = parsed_data.get("teacher_response", "")
            problem_id = parsed_data.get("problem_id", "")
            logging.log(f"\nExtracted teacher_response: {teaching_response}\nExtracted problem_id_match: {problem_id}\n", logger, 2)
            
            # Only try to get problem if problem_id is not empty
            if problem_id and problem_id.strip():
                display_problem, problem, solution = problem_handler.get_problem(problem_id)
                if not problem:
                    logging.log(f"Problem not found for ID: {problem_id}", logger, 2)
                    problem = ""
                    display_problem = ""
                    solution = ""
            else:
                logging.log(f"Empty problem_id provided, skipping problem retrieval", logger, 2)
                problem = ""
                display_problem = ""
                solution = ""

            context_response = str(teaching_response) + str(problem)
            teaching_response = str(teaching_response) + str(display_problem)
            
            logging.log(f"Teaching response with problem: {teaching_response}", logger, 2)

    except json.JSONDecodeError:
        # Fallback: Try to extract from structured text format
        teaching_match = re.search(r'teacher_response":\s*(.*?)(?=,\s*"problem_id|$)', text, re.DOTALL)
        problem_id_match = re.search(r'problem_id":\s*"([^"]+)"', text, re.DOTALL)
        logging.log(f"Found regex match!\nExtracted teacher_response: {teaching_match}\nExtracted problem_id_match: {problem_id_match}\n", logger, 2)
        if problem_id_match:
            problem_id = problem_id_match.group(1).strip()  
            
            # Only try to get problem if problem_id is not empty
            if problem_id and problem_id.strip():
                display_problem, problem, solution = problem_handler.get_problem(problem_id)
                if not problem:
                    logging.log(f"Problem not found for ID: {problem_id}", logger, 2)
                    problem = ""
                    display_problem = ""
                    solution = ""
            else:
                logging.log(f"Empty problem_id provided, skipping problem retrieval", logger, 2)
                problem = ""
                display_problem = ""
                solution = ""

        if teaching_match:
            teaching_response = teaching_match.group(1).strip()
            context_response = str(teaching_response) + str(problem)
            teaching_response = str(teaching_response) + str(display_problem)
            logging.log(f"Teaching response with problem: {teaching_response}", logger, 2)

    if problem:
        logging.log(f"Using Solution: {solution}\nUsing Raw Problem: {problem}", logger, 2)

    # Error handling logic
    if teaching_response:
        return teaching_response, context_response, problem, solution
    else:
        logging.log("Teacher response not found, using default", logger, 2)
        return default_response, default_response, problem, solution
    

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


def format_eval(eval_result):
    """Format the evaluation result to extract Student Analysis"""
    student_analysis = ""  # Initialize with default value
    
    if isinstance(eval_result, dict):
        if "Student Analysis" in eval_result.keys():
            student_analysis = eval_result.get("Student Analysis", "")
    else:
        try:
            parsed_response = json.loads(eval_result)
            if isinstance(parsed_response, dict):
                student_analysis = parsed_response.get("Student Analysis", "")
        except:
            analysis_match = re.search(r'"Student Analysis":\s*"([^"]*(?:\\.[^"]*)*)"', eval_result, re.DOTALL)
            if analysis_match:
                student_analysis = analysis_match.group(1).strip()
            else:
                logging.log("No analysis match found in regex search", logger, 0)
    
    return student_analysis


def format_grade(eval_result):
    """Format the evaluation result to extract Evaluation of Concepts"""
    eval_grade = {}  # Initialize with default value
    
    if isinstance(eval_result, dict):
        if "Evaluation of Concepts" in eval_result.keys():
            eval_grade = eval_result.get("Evaluation of Concepts", {})
            if not isinstance(eval_grade, dict):
                try:
                    eval_grade = json.loads(eval_grade)
                except json.JSONDecodeError:
                    logging.log("Failed to parse eval grade JSON", logger, 0)
    else:
        try:
            parsed_response = json.loads(eval_result)
            if isinstance(parsed_response, dict):
                eval_grade = parsed_response.get("Evaluation of Concepts", {})
                if not isinstance(eval_grade, dict):
                    try:
                        eval_grade = json.loads(eval_grade)
                    except json.JSONDecodeError:
                        logging.log("Failed to parse eval grade JSON", logger, 0)
        except:
            grade_match = re.search(r'"Evaluation of Concepts":\s*(\{(?:[^{}]|{[^{}]*})*\})', eval_result, re.DOTALL)
            if grade_match:
                if not isinstance(grade_match.group(1), dict):
                    try:
                        eval_grade = json.loads(grade_match.group(1))
                    except json.JSONDecodeError:
                        logging.log("Failed to parse eval grade JSON", logger, 0)
                else:
                    eval_grade = grade_match.group(1)
            else:
                # No grade match found, keep default empty dict
                logging.log("No grade match found in regex search", logger, 0)
    
    # Filter out keys not in amc8_concepts
    eval = eval_grade.copy()
    for key in eval.keys():
        if key not in knowledge_info.amc8_concepts:
            del eval_grade[key]

    return eval_grade


    
    # Helper function to extract and stream only the value from JSON
def extract_json_value(buffer: str, key: str) -> tuple[str, int]:
    """
    Try to parse JSON from buffer and extract value for given key.
    Returns (value_string, length_used) where length_used is how many chars of buffer
    have been successfully parsed into the value.
    """
    try:
        # Try to parse the buffer as JSON
        parsed = json.loads(buffer)
        if key in parsed:
            value = str(parsed[key])
            return value, len(buffer)
    except (json.JSONDecodeError, KeyError):
        # JSON might be incomplete, try to extract value using string matching
        # Look for pattern like "key": "value..."
        # Pattern to match: "key": "value" or "key": "value...
        pattern = rf'"{re.escape(key)}"\s*:\s*"([^"]*)"'
        match = re.search(pattern, buffer)
        if match:
            # Found complete value in quotes
            return match.group(1), match.end()
        
        # Pattern for incomplete value: "key": "value...
        pattern_incomplete = rf'"{re.escape(key)}"\s*:\s*"([^"]*)'
        match = re.search(pattern_incomplete, buffer)
        if match:
            # Found partial value (not yet closed)
            return match.group(1), len(buffer)
    
    return "", 0


def convert_redis_messages(messages: List[Any]) -> List[BaseMessage]:
    """
    Convert a LangChain-serialized messages list (e.g., items with keys 'lc', 'type', 'id', 'kwargs')
    into a list of BaseMessage instances compatible with LangGraph add_messages.

    Examples of accepted input items:
      { 'lc': 1, 'type': 'constructor', 'id': ['langchain','schema','messages','HumanMessage'], 'kwargs': {...} }
      { 'lc': 1, 'type': 'constructor', 'id': ['langchain','schema','messages','AIMessage'], 'kwargs': {...} }
      { 'role': 'user'|'assistant', 'content': '...'}
    """
    # Empty or invalid list
    if not isinstance(messages, list) or len(messages) == 0:
        return []

    # If already BaseMessage instances, return as-is
    try:
        if all(isinstance(m, BaseMessage) for m in messages):
            logging.log(f"Messages already converted to BaseMessage instances, using as is.", logger, 2)
            return messages  # type: ignore[return-value]
    except Exception:
        pass

    converted: List[BaseMessage] = []
    try:
        for m in messages:
            if "HumanMessage" in m.get("id"):
                converted.append(HumanMessage(content=m.get("kwargs").get("content")))
            elif "AIMessage" in m.get("id"):
                converted.append(AIMessage(content=m.get("kwargs").get("content")))
            else:
                logging.log(f"Unknown message type: {m.get('id')}", logger, 0)
                converted.append(HumanMessage(content=m.get("kwargs").get("content")))

        return converted

    except Exception as e:
        logging.log(f"Error converting messages to BaseMessage instances: {e}", logger, 0)
        return []



def get_list_of_obj(lesson_state, mastery):
    for key,value in lesson_state.items():
        if value.lower() == 'in progress':
            if key.lower() == "start_lesson":
                return """1. Greet the student
                          2. Introduce the lesson topic
                          3. Ask them if they are ready to begin"""
            if key.lower() in ["give_first_problem", "give_second_problem", "give_third_problem"]:
                if mastery < 0.3:
                    return """1. Give the student a easier problem (around difficulty 1-2) using the get_problem tool to introduce them to the concept you are covering."""
                elif mastery < 0.6:
                    return """1. Give the student a medium problem (around difficulty 3-4) using the get_problem tool to introduce them to the concept you are covering."""
                else:
                    return """1. Give the student a harder problem (around difficulty 4-5) using the get_problem tool to introduce them to the concept you are covering."""
            if key.lower() in ["first_problem_walkthrough", "second_problem_walkthrough", "third_problem_walkthrough"]:
                return """1. Interactively go through the problem with the student"""
            if key.lower() == "end_lesson":
                return """1. Wrap up the lesson: briefly summarize what you covered in the lesson 
                          2. Ask if they have any further questions
                          3. Say goodbye to the student"""
            if key.lower() == "check":
                return """1. Give the student a difficult problem (difficulty 4-5) using the get_problem tool to ensure their understanding before they can move on to the next learning objective"""
            if key.lower() == "behind":
                return """1. The student is lacking in this learning objective, address those gaps with the student
                          2. Give the student a problem using the get_problem tool for them to solve to overcome this gap in their understanding"""

def parse_lesson_tracker_response(response):
    lesson_state = {
        'START_LESSON': 'Done', 
        'GIVE_FIRST_PROBLEM': 'Done',
        'FIRST_PROBLEM_WALKTHROUGH': 'Done',
        'GIVE_SECOND_PROBLEM': 'In Progress',
        'SECOND_PROBLEM_WALKTHROUGH': 'Not Done',
        'GIVE_THIRD_PROBLEM': 'Not Done',
        'THIRD_PROBLEM_WALKTHROUGH': 'Not Done',
        'END_LESSON': 'Not Done'
    }
    current_obj = "none"
    
    try:
        # Try to parse as JSON first
        parsed_data = json.loads(response)
        if isinstance(parsed_data, dict):
            # logging.log("Parsed response as json!", logger, 2)
            lesson_state = parsed_data.get("lesson_state", "")
            current_obj = parsed_data.get("current_obj", "")
            logging.log(f"\nExtracted lesson_state: {lesson_state}\nExtracted current_obj: {current_obj}\n", logger, 2)

    except json.JSONDecodeError:
        # Fallback: Try to extract from structured text format
        lesson_state_match = re.search(r'lesson_state":\s*(.*?)(?=,\s*"current_obj|$)', response, re.DOTALL)
        current_obj_match = re.search(r'current_obj":\s*(\{.*?\})', response, re.DOTALL)
        logging.log(f"Found regex match!\nExtracted lesson_state: {lesson_state_match}\nExtracted current_obj: {current_obj_match}\n", logger, 2)
        if current_obj_match:
            current_obj = current_obj_match.group(1).strip()  
        if lesson_state_match:
            lesson_state = lesson_state_match.group(1).strip()

    lesson_state = check_lesson_state(lesson_state)
    # Error handling logic
    return lesson_state, current_obj

def get_current_state(lesson_state):
    for key,value in lesson_state.items():
        if value.lower() == 'in progress':
            return key
    return None