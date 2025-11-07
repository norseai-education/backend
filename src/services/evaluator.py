from langchain.agents import create_react_agent, AgentExecutor
from src.services.state import State
import json
from src.utils import utils
from src.utils import logging
from src.utils import knowledge_info
import re


# Configure logging
logger = logging.set_logger(__name__)

class EvaluatorModel:
    def __init__(self, model, prompt, list_of_tools):
        self.model = model
        self.prompt = prompt
        self.tools = list_of_tools

    def build_node(self, state: State): 
        # logging.log(f"Current state: {state}", logger, 2)
        logging.log(f"Going through evaluator node...", logger, 2)
        student_input = state["messages"][-1].content
        learning_objective = state.get("cur_learning_objective", "DEFAULT")
        solution = state.get("solution", "no solution provided")
        context = utils.format_conversation_context(state["messages"][-4:])
        cur_problem = state.get("cur_problem", "no problem provided")
        logging.log(f"Inputs of Evaluator: \ninput: {student_input}\ncur_problem: {cur_problem}\nsolution: {solution}", logger, 2)

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
            "context": context,
            "cur_problem": cur_problem,
            "solution": solution
        })
        
        raw_response = response["output"]
        logging.log(f"Raw response: {raw_response}", logger, 2)
        grade, evaluation = utils.format_eval_output(raw_response)

        logging.log(f"Formatted evaluator grade: {grade}\nFormatted evaluation: {evaluation}", logger, 2)

        return {
            "evaluator_grade": grade,
            "evaluation": evaluation
        }

        


