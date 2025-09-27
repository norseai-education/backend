from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID

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

class AssessmentSubmitRequest(BaseModel):
    student_answers: list[dict[str, str]]  # [{"problem_id": <id>, "student_answer": <student_answer>}, ...]

class AssessmentStoreRequest(BaseModel):
    student_answers: list[dict[str, Any]]  # [{"problem_id": <id>, "student_answer": <student_answer>, "time_spent_seconds": <float>},...]

class UserGraphRequest(BaseModel):
    user_graph: Optional[dict[str, float]] = None  # {"concept1": <probability>, "concept2": <probability>, ...} Provide if is an assessment given at the end of a lesson, otherwise will just user default graph

class ClassRequest(BaseModel):
    class_id: UUID

class CreateClassRequest(BaseModel):
    class_name: str
    class_description: str

