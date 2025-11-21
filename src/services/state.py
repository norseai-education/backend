from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    classification: str
    init_learning_objective: str
    cur_learning_objective: str # need to initialize this at the beginning based on student info
    learning_status: str
    student_id: int
    lesson_state: dict[str, str]
    messages: Annotated[list, add_messages]
    grade: dict[str, str]
    evaluation: str
    solution: str
    bkt_graph: dict[str, list]  #bkt_graph: dict[str, dict[str, float]] | None for multiple topics i.e. alg, geo, number theory etc.
    # math_context: str
    # personality_context: str
    cur_mastery: list[str]
    display_response: str
    cur_problem: str
    current_obj: str

