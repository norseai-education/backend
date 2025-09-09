from pydantic import BaseModel
from typing import Optional

class ChatMessage(BaseModel):
    message: str
    student_id: int

class UserSignup(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    message: str

class AssessmentRequest(BaseModel):
    student_answers: list[dict[str, str]]  # [{"problem_id": <id>, "answer": <student_answer>}, ...]
    start_time: Optional[float] = None

class UserGraphRequest(BaseModel):
    user_graph: Optional[dict[str, float]] = None  # {"concept1": <probability>, "concept2": <probability>, ...} Provide if is an assessment given at the end of a lesson, otherwise will just user default graph