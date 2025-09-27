from langchain.agents import create_react_agent, AgentExecutor
from backend.src.services.state import State
from backend.src.utils import logging
from backend.src.utils import utils

# Configure logging
logger = logging.set_logger(__name__)

class MathTeacher:
    def __init__(self, model, prompt, store, list_of_tools):
        self.model = model
        self.prompt = prompt
        self.store=store
        self.store.connect("amc8_database")
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
        logging.log(f"Context formatted: {formatted_context}", logger, 2)
        return formatted_context

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

        logging.log(f"Raw response: \n{raw_response}\n type: {type(raw_response)}", logger, 2)

        new_lesson_state, final_response = utils.parse_response(response["output"])
        
        # add teacher response to math-related-db
        utils.store_input(self.store, 'math_related', student_id, final_response)

        return {"messages": [{"role": "assistant", "content": final_response}],
                "lesson_state": new_lesson_state
                }

    
