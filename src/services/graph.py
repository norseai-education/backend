from backend.src.services.nodes import Nodes
from backend.src.services.state import State
from langgraph.graph import StateGraph, START, END

class BuildNorseAIGraph:
    def __init__(self):
        self.nodes = Nodes()
    
    def get_graph(self):
        graph_builder = StateGraph(State)

        # add nodes
        graph_builder.add_node("classifier", self.nodes.classifier_node)
        graph_builder.add_node("evaluator", self.nodes.evaluator_node)
        graph_builder.add_node("bkt", self.nodes.bkt_node)
        graph_builder.add_node("math_rag", self.nodes.math_rag_node)
        graph_builder.add_node("personality_rag", self.nodes.personality_rag_node)
        graph_builder.add_node("math_teacher", self.nodes.math_teacher_node)
        graph_builder.add_node("teacher", self.nodes.teacher_node)

        # add edges
        graph_builder.add_edge(START, "classifier")
        graph_builder.add_conditional_edges(
        "classifier",
        lambda state: state.get("classification"),
        {"mathematical": "evaluator", "non-mathematical": "personality_rag"}
        )
        graph_builder.add_conditional_edges(
            "evaluator",
            lambda state: (
                "no-bkt" if (
                    isinstance(state.get("lesson_state"), dict) and (
                        state["lesson_state"].get("START_LESSON", "").lower() == "in progress" or
                        state["lesson_state"].get("END_LESSON", "").lower() == "in progress"
                    )
                ) else "bkt"
            ),
            {"no-bkt": "math_rag", "bkt": "bkt"}
        )

        # graph_builder.add_edge("evaluator", "bkt")
        graph_builder.add_edge("bkt", "math_rag")

        graph_builder.add_edge("math_rag","math_teacher")

        graph_builder.add_edge("personality_rag", "teacher")
        graph_builder.add_edge("math_teacher", END)
        graph_builder.add_edge("teacher", END)
    
        return graph_builder




