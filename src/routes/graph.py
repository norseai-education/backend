from fastapi import APIRouter
from fastapi import status
from backend.src.models.requests import UserGraphRequest
from backend.src.models.responses import UserGraphResponse, MessageResponse
from backend.src.services.graph_service import UserGraphService

router = APIRouter()
user_graph_service = UserGraphService()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@router.get("/user_graph/{student_id}", response_model=UserGraphResponse)
async def get_user_graph(student_id: int):
    graph = await user_graph_service.get(student_id)
    return UserGraphResponse(user_graph=graph)

@router.post("/update_user_graph/{student_id}", response_model=MessageResponse)
async def update_user_graph(student_id: int, request: UserGraphRequest):
    update = await user_graph_service.update(student_id, request.user_graph)
    return MessageResponse(message="User graph updated successfully")

@router.delete("/delete_user_graph/{student_id}", response_model=MessageResponse)
async def delete_user_graph(student_id: int):
    delete = await user_graph_service.delete(student_id)
    return MessageResponse(message="User graph deleted successfully")