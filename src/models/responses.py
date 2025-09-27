from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID

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

class GiveAssessmentResponse(BaseModel):
    problems: list[dict[Any, Any]]  # [{"problem_id": <id>, "problem_number": <number>, "problem": <text>}, ...]
    number_problems: int

class AssessmentResultResponse(BaseModel):
    solutions: list[dict[Any, Any]] # [{"problem_id": <id>, "correct": <bool>, "correct_answer": str, "solution": <solution_text>}, ...]
    total_correct: int

class AssessmentStoreResponse(BaseModel):
    assessment_id: str # assessment identifier

class AssessmentRetrieveResponse(BaseModel):
    problems: list[dict[Any, Any]]  # [{"problem_id": <id>, "problem_number": <number>, "problem": <text>, "student_answer": <answer>, "correct_answer": <correct_answer>}, ...]
    number_problems: int
    number_correct: int

class UserGraphResponse(BaseModel):
    user_graph: Dict[str, float]  # {"concept1": <probability>, "concept2": <probability>, ...}
    
class RouteResponse(BaseModel):
    give_assessment: bool

class ClassesResponse(BaseModel):
    class_ids: list[UUID]
    class_names: list[str]
    class_descriptions: list[str]