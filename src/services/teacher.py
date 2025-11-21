from src.services.state import State
from langchain.agents import create_react_agent, AgentExecutor
from src.utils import logging
from src.utils import utils

# Configure logging
logger = logging.set_logger(__name__)

class Teacher:
    def __init__(self, model, prompt, list_of_tools):
        #initialize storing to mongodb for personality
        # self.store=store
        # self.store.connect("amc8_database")

        self.model = model
        self.prompt = prompt
        self.tools = list_of_tools

    def build_node(self, state: State):
        # logging.log(f"Current state: \n{state}", logger, 2)
        logging.log(f"Going through teacher node...", logger, 2)
        # Get the last message content, handling both AIMessage objects and dictionaries
        student_input = state["messages"][-1].content

        student_id = state.get("student_id")

        # add student input to persona db
        # utils.store_input(self.store, 'student_persona',student_id, student_input)

        learning_objective = state.get("cur_learning_objective", "DEFAULT")
        # personality_context = state.get("personality_context", "DEFAULT")
        solution = state.get("solution", "no solution provided")
        current_problem = state.get("cur_problem", "no problem currently")
        evaluation = state.get("evaluation", "no evaluation provided")
        lesson_state = state.get("lesson_state")
        learning_status = state.get("learning_status")
        cur_mastery = state.get("cur_mastery")
        bkt_graph = state.get("bkt_graph")
        context = state["messages"]
        logging.log(f"Context messages: \n{context}", logger, 2)
        current_obj = state.get("current_obj")
        current_state = utils.get_current_state(lesson_state)
        # logging.log(f"Context messages: \n{context}", logger, 2)

        teacher_prompt = self.prompt.get_prompt(lesson_state, learning_status, bkt_graph.get(learning_objective))
        
        # Format the prompt with actual values to see what the LLM receives
        try:
            # Get tool names for formatting
            tool_names = [tool.name for tool in self.tools] if self.tools else []
            tools_description = str([tool.name for tool in self.tools]) if self.tools else "[]"
            
            # Format the prompt with available variables
            formatted_messages = teacher_prompt.format_messages(
                student_input=student_input,
                learning_objective=learning_objective,
                # personality_context=personality_context,
                current_obj = current_obj,
                current_state = current_state,
                context=context,
                solution=solution,
                cur_problem=current_problem,
                evaluation=evaluation,
                # lesson_state=lesson_state,
                student_id=student_id,
                cur_mastery=cur_mastery,
                tools=tools_description,
                tool_names=", ".join(tool_names) if tool_names else "",
                agent_scratchpad=""  # This will be empty initially, filled by agent executor
            )
            
            # Convert formatted messages to readable string for logging
            formatted_prompt_parts = []
            for i, msg in enumerate(formatted_messages):
                msg_type = getattr(msg, 'type', 'unknown')
                if hasattr(msg, 'content'):
                    content = msg.content
                elif hasattr(msg, 'get_content'):
                    content = msg.get_content()
                else:
                    content = str(msg)
                
                formatted_prompt_parts.append(f"{'='*80}\nMESSAGE {i+1} - {msg_type.upper()}:\n{'-'*80}\n{content}")
            
            formatted_prompt_str = "\n\n" + "\n".join(formatted_prompt_parts) + "\n\n" + "="*80
            logging.log(f"Teacher prompt (formatted with variables): \n{formatted_prompt_str}", logger, 2)
        except Exception as e:
            # Fallback to logging the template if formatting fails
            logging.log(f"Teacher prompt (template): \n{teacher_prompt}", logger, 2)
            logging.log(f"Error formatting prompt: {e}", logger, 2)

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
            # "personality_context": personality_context,
            "current_obj": current_obj,
            "current_state": current_state,
            "context": context,
            "solution": solution,
            "cur_problem": current_problem,
            "evaluation": evaluation,
            # "lesson_state": lesson_state,
            "student_id": student_id,
            "cur_mastery": cur_mastery
            }
        )
        raw_response = response["output"]

        logging.log(f"Raw response: \n{raw_response}", logger, 2)

        display_response, context_response, raw_problem, problem_solution = utils.parse_response(raw_response)

        # final_response = utils.parse_problem(final_response)
        if problem_solution and raw_problem:
            return {"messages": [{"role": "assistant", "content": context_response}],
                    "display_response": display_response,
                    "cur_problem": raw_problem,
                    "solution": problem_solution
                    }
        else:
            return {"messages": [{"role": "assistant", "content": context_response}],
                    "display_response": display_response}
