from langchain.agents import create_react_agent, AgentExecutor
from src.services.state import State
from src.utils import logging
from src.utils import utils

# Configure logging
logger = logging.set_logger(__name__)

class MathTeacher:
    def __init__(self, model, prompt, store, list_of_tools):
        self.model = model
        self.prompt = prompt
        self.store=store
        self.store.connect("amc8_database")
        self.tools = list_of_tools

    def build_node(self, state: State):
        logging.log(f"Current state: \n{state}", logger, 2)
        logging.log(f"Going through math teacher node...", logger, 2)
        student_input = state["messages"][-1]
        learning_objective = state.get("cur_learning_objective", "DEFAULT")
        solution = state.get("solution", "DEFAULT")
        math_context = state.get("math_context", "DEFAULT")
        student_id = state.get("student_id", "default_student")
        lesson_state = state.get("lesson_state")
        learning_status = state.get("learning_status")
        context = utils.format_conversation_context(state["messages"])
        cur_mastery = state.get("cur_mastery")
        bkt_graph = state.get("bkt_graph")

        teacher_prompt = self.prompt.get_prompt(lesson_state, learning_status, bkt_graph.get(learning_objective))
        

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

        logging.log("Getting math teacher response...", logger, 2)

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

        logging.log(f"Raw response: \n{raw_response}", logger, 2)

        new_lesson_state, final_response = utils.parse_response(raw_response)
        
        # if problem then use display problem
        # final_response = utils.parse_problem(final_response)

        # add teacher response to math-related-db
        utils.store_input(self.store, 'math_related', student_id, final_response)

        return {"messages": [{"role": "assistant", "content": final_response}],
                "lesson_state": new_lesson_state
                }

    
