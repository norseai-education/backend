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
        # logging.log(f"Current state: \n{state}", logger, 2)
        logging.log(f"Going through math teacher node...", logger, 2)
        student_input = state["messages"][-1].content
        learning_objective = state.get("cur_learning_objective", "triangles")
        solution = state.get("solution", "no solution provided")
        evaluation = state.get("evaluation", "no evaluation provided")
        math_context = state.get("math_context", "no math context")
        student_id = state.get("student_id", "1")
        lesson_state = state.get("lesson_state")
        learning_status = state.get("learning_status")
        context = state["messages"]
        cur_mastery = state.get("cur_mastery")
        bkt_graph = state.get("bkt_graph")

        teacher_prompt = self.prompt.get_prompt(lesson_state, learning_status, bkt_graph.get(learning_objective))
        logging.log(f"Math teacher prompt: \n{teacher_prompt}", logger, 2)
        

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
            "evaluation": evaluation,
            "math_context": math_context,
            "context": context,
            "lesson_state": lesson_state,
            "cur_mastery": cur_mastery
            }
        )

    
        raw_response = response["output"]

        logging.log(f"Raw response: \n{raw_response}", logger, 2)

        new_lesson_state, display_response, context_response, raw_problem, problem_solution = utils.parse_response(raw_response)

        # add teacher response to math-related-db
        utils.store_input(self.store, 'math_related', student_id, context_response)

        if problem_solution and raw_problem:
            return {"messages": [{"role": "assistant", "content": context_response}],
                    "lesson_state": new_lesson_state,
                    "display_response": display_response,
                    "cur_problem": raw_problem,
                    "solution": problem_solution
                    }
        else:
            return {"messages": [{"role": "assistant", "content": context_response}],
                    "lesson_state": new_lesson_state,
                    "display_response": display_response}

    
