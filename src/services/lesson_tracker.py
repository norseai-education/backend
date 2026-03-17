from langchain.agents import create_react_agent, AgentExecutor
from src.services.state import State
from src.utils import logging
from src.utils import utils

# Configure logging
logger = logging.set_logger(__name__)

class LessonTracker:
    def __init__(self, model, prompt, list_of_tools):
        self.model = model
        self.prompt = prompt
        self.tools = list_of_tools

    def build_node(self, state: State):
        # logging.log(f"Current state: \n{state}", logger, 2)
        logging.log(f"Going through lesson tracker node...", logger, 2)
        student_input = state["messages"][-1].content
        learning_objective = state.get("cur_learning_objective", "triangles")
        evaluation = state.get("evaluation", "no evaluation provided")
        bkt_graph = state.get("bkt_graph")
        student_id = state.get("student_id", "1")
        lesson_state = state.get("lesson_state")
        list_of_obj = utils.get_list_of_obj(lesson_state, bkt_graph.get(learning_objective))
        current_obj = state.get('current_obj', "none")
        context = state["messages"]
        logging.log(f"Objectives List: {list_of_obj}", logger, 2)
        logging.log(f"Current Objective: {current_obj}", logger, 2)
        

        agent = create_react_agent(
            llm=self.model,
            tools=self.tools,
            prompt=self.prompt
        )

        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=5
        )

        logging.log("Getting lesson tracker response...", logger, 2)

        response = agent_executor.invoke({                                            # Inputs: student_input, learning_objective, solution, math_context | Outputs: response
            "student_input": student_input,
            "student_id": student_id,
            "learning_objective": learning_objective,
            "evaluation": evaluation,
            "context": context,
            "lesson_state": lesson_state,
            "current_obj": current_obj,
            "list_of_obj": list_of_obj
            }
        )

    
        raw_response = response["output"]

        logging.log(f"Raw lesson tracker response: \n{raw_response}", logger, 2)

        new_lesson_state, new_current_obj = utils.parse_lesson_tracker_response(raw_response)

        return {
                "lesson_state": new_lesson_state,
                "current_obj": new_current_obj
                }


    
