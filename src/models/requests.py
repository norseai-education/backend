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