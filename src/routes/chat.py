from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.src.models.requests import ChatRequest, AssessmentRequest
from backend.src.models.responses import MessageResponse, ChatStatusResponse, RouteResponse
from backend.src.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()

@router.post("/init/{student_id}", response_model=RouteResponse)
async def init_chat(student_id: int):
    """Initialize chat session for student"""
    route = await chat_service.initialize_session(student_id)
    if route:
        return RouteResponse(route = "/chat")
    return MessageResponse(route = "/assessment")

@router.post("/s/{student_id}")
async def chat_stream(student_id: int, message_data: ChatRequest):
    """Stream chat response"""
    message = message_data.message.strip()
    
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    async def event_generator():
        async for chunk in chat_service.get_chat_response(student_id, message):
            yield chunk
    
    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@router.delete("/session/{student_id}", response_model=MessageResponse)
async def end_chat_session(student_id: int):
    """Manually end chat session"""
    message = await chat_service.end_session(student_id)
    return MessageResponse(message=message)

@router.get("/status/{student_id}", response_model=ChatStatusResponse)
async def get_chat_status(student_id: int):
    """Get current student status"""
    status = chat_service.get_session_status(student_id)
    return ChatStatusResponse(**status)