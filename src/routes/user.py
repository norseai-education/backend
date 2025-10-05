from fastapi import APIRouter, Depends
from fastapi import status
from src.models.requests import StudentIDRequest
from src.models.responses import StudentIDResponse
from src.services.user_service import UserService
from src.core.dependencies import get_db_connection
import asyncpg

router = APIRouter()
user_service = UserService()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@router.post("/get_student_id", response_model=StudentIDResponse)
async def get_available_classes(request: StudentIDRequest, conn: asyncpg.Connection = Depends(get_db_connection)):
    student_id = await user_service.get_student_id(conn, request.email)
    return StudentIDResponse(student_id=student_id)
