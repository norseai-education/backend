from langchain.agents import create_react_agent, AgentExecutor
from backend.src.services.state import State
import json
from backend.src.utils import logging
import re


# Configure logging
logger = logging.set_logger(__name__)

class EvaluatorModel:
    def __init__(self, model, prompt, list_of_tools):
        self.model = model
        self.prompt = prompt
        self.tools = list_of_tools

        
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
        return formatted_context

    def format_eval_output(self, eval_result):
        """Format the evaluation result to extract grade and solution"""
        if isinstance(eval_result, dict):
            if "Evaluation of Concepts" and "Solution" in eval_result.keys():
                solution = parsed_response.get("Solution","")
                eval_grade = parsed_response.get("Evaluation of Concepts",{})
                if not isinstance(eval_grade, dict):
                    try:
                        eval_grade = json.loads(eval_grade)
                    except json.JSONDecodeError:
                        logging.log("Failed to parse eval grade JSON", logger, 0)
                        eval_grade = {}
                return eval_grade, solution
        try:
            parsed_response = json.loads(eval_result)
            if isinstance(parsed_response, dict):
                solution = parsed_response.get("Solution","")
                eval_grade = parsed_response.get("Evaluation of Concepts",{})
                if not isinstance(eval_grade, dict):
                    try:
                        eval_grade = json.loads(eval_grade)
                    except json.JSONDecodeError:
                        logging.log("Failed to parse eval grade JSON", logger, 0)
                        eval_grade = {}
        except json.JSONDecodeError:
            grade_match = re.search(r'Evaluation of Concepts:\s*(.*?)(?=Solution:|$)', eval_result, re.DOTALL)
            solution_match = re.search(r'Solution:\s*(\{.*\})', eval_result, re.DOTALL)

            if solution_match:
                solution = solution_match.group(1).strip()
            
            if grade_match:
                try:
                    eval_grade = json.loads(grade_match.group(1))
                except json.JSONDecodeError:
                    logging.log("Failed to parse eval grade JSON", logger, 0)
                    eval_grade = {}
        
        eval = eval_grade.copy()
        for key in eval.keys():
            if key not in logging.concepts:
                del eval_grade[key]
        if solution:
            return eval_grade, solution
        else:
            logging.log("Failed to find eval solution", logger, 0)
            return eval_grade, ""

    def build_node(self, state: State): 
        logging.log(f"Current state: {state}", logger, 2)
        logging.log(f"Going through evaluator node...", logger, 2)
        student_input = state["messages"][-1].content
        learning_objective = state.get("cur_learning_objective", "DEFAULT")
        context = self.format_conversation_context(state["messages"][-4:])
        logging.log(f"Inputs of Evaluator: \ninput: {student_input}\nlearning_obj: {learning_objective}\ncontext: {context}", logger, 2)

        # Create and run agent
        agent = create_react_agent(
            llm=self.model,
            tools=self.tools,
            prompt=self.prompt
        )

        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )

        response = agent_executor.invoke({
            "student_input": student_input,
            "learning_objective": learning_objective,
            "context": context
        })
        
        raw_response = response["output"]
        logging.log(f"Raw response: {raw_response}", logger, 2)
        grade, solution = self.format_eval_output(response["output"])

        logging.log(f"Formatted evaluator grade: {grade}\nFormatted evaluator solution: {solution}", logger, 2)

        return {
            "evaluator_grade": grade,
            "evaluator_solution": solution
        }

        


