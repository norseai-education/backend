from pydantic import BaseModel
from typing import Optional
from bson import ObjectId

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
    student_answers: dict[ObjectId: str]  # Mapping of problem_id to student's answer
    student_id: int