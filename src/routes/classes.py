from fastapi import APIRouter, Depends
from fastapi import status
from src.models.requests import ClassRequest, CreateClassRequest
from src.models.responses import ClassesResponse, MessageResponse
from src.services.class_service import ClassService
from src.core.dependencies import get_db_connection
import asyncpg

router = APIRouter()
class_service = ClassService()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@router.get("/available_classes", response_model=ClassesResponse)
async def get_available_classes(conn: asyncpg.Connection = Depends(get_db_connection)):
    classes = await class_service.get_available_classes(conn)
    class_ids = [record['id'] for record in classes]
    class_names = [record['class_name'] for record in classes]
    class_descriptions = [record['description'] for record in classes]
    return ClassesResponse(class_ids=class_ids, class_names=class_names, class_descriptions=class_descriptions)

@router.post("/add_class/{student_id}", response_model=MessageResponse)
async def register_class(student_id: int, request: ClassRequest, conn: asyncpg.Connection = Depends(get_db_connection)):
    add_class = await class_service.register_class(conn, student_id, request.class_id)
    return MessageResponse(message=f"Class {add_class} registered for student {student_id} successfully")

@router.delete("/remove_class/{student_id}", response_model=MessageResponse)
async def remove_class(student_id: int, request: ClassRequest, conn: asyncpg.Connection = Depends(get_db_connection)):
    remove_class = await class_service.remove_class(conn, student_id, request.class_id)
    return MessageResponse(message=f"Class {remove_class} removed for student {student_id} successfully")

@router.get("/my_classes/{student_id}", response_model=ClassesResponse)
async def get_user_classes(student_id: int, conn: asyncpg.Connection = Depends(get_db_connection)):
    classes = await class_service.get_user_classes(conn, student_id)
    class_ids = [record['class_id'] for record in classes]
    class_names = [record['class_name'] for record in classes]
    class_descriptions = [record['description'] for record in classes]
    return ClassesResponse(class_ids=class_ids, class_names=class_names, class_descriptions=class_descriptions)

@router.post("/create_class", response_model=MessageResponse)
async def create_class(request: CreateClassRequest, conn: asyncpg.Connection = Depends(get_db_connection)):
    create = await class_service.create_class(conn, request.class_name, request.class_description)
    return MessageResponse(message=f"Class {create} created successfully")