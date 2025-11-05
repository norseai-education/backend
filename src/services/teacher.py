from src.services.state import State
from langchain.agents import create_react_agent, AgentExecutor
from src.utils import logging
from src.utils import utils

# Configure logging
logger = logging.set_logger(__name__)

class Teacher:
    def __init__(self, model, prompt, store, list_of_tools):
        #initialize storing to mongodb for personality
        self.store=store
        self.store.connect("amc8_database")

        self.model = model
        self.prompt = prompt
        self.tools = list_of_tools

    def build_node(self, state: State):
        logging.log(f"Current state: \n{state}", logger, 2)
        logging.log(f"Going through teacher node...", logger, 2)
        # Get the last message content, handling both AIMessage objects and dictionaries
        student_input = state["messages"][-1].content

        student_id = state.get("student_id")

        # add student input to persona db
        utils.store_input(self.store, 'student_persona',student_id, student_input)

        learning_objective = state.get("cur_learning_objective", "DEFAULT")
        personality_context = state.get("personality_context", "DEFAULT")
        solution = state.get("solution", "no solution provided")
        evaluation = state.get("evaluation", "no evaluation provided")
        lesson_state = state.get("lesson_state")
        learning_status = state.get("learning_status")
        cur_mastery = state.get("cur_mastery")
        bkt_graph = state.get("bkt_graph")
        context = state["messages"]

        logging.log("Getting teacher prompt", logger, 2)
        teacher_prompt = self.prompt.get_prompt(lesson_state, learning_status, bkt_graph.get(learning_objective))

        agent = create_react_agent(
            llm=self.model,
            tools=self.tools,
            prompt=teacher_prompt
        )

        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

        logging.log("Getting teacher response...", logger, 2)

        response = agent_executor.invoke({                                            # Inputs: student_input, learning_objective, solution, math_context | Outputs: response
            "student_input": student_input,
            "learning_objective": learning_objective,
            "personality_context": personality_context,
            "context": context,
            "solution": solution,
            "evaluation": evaluation,
            "lesson_state": lesson_state,
            "student_id": student_id,
            "cur_mastery": cur_mastery
            }
        )
        raw_response = response["output"]

        logging.log(f"Raw response: \n{raw_response}", logger, 2)

        new_lesson_state, display_response, context_response, raw_problem, problem_solution = utils.parse_response(raw_response)

        # final_response = utils.parse_problem(final_response)
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
