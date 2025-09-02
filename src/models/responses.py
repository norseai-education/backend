from pydantic import BaseModel
from typing import Optional, Dict, Any
from bson import ObjectId

class ChatResponse(BaseModel):
    response: str
    student_id: int

class AuthResponse(BaseModel):
    message: str
    session_token: str
    student_id: int

class UserInfoResponse(BaseModel):
    authenticated: bool
    username: Optional[str] = None
    student_id: Optional[int] = None

class ChatStatusResponse(BaseModel):
    active: bool
    message_count: Optional[int] = None
    lesson_state: Optional[Dict[str, Any]] = None
    current_objective: Optional[str] = None

class MessageResponse(BaseModel):
    message: str

class AssessmentResponse(BaseModel):
    problems: Optional[dict[ObjectId: str]] = None  # Mapping of problem_id to problem text
    student_score: Optional[list] = None
    student_id: int

class RouteResponse(BaseModel):
    route: str