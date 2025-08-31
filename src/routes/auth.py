from fastapi import APIRouter, Request, Depends, HTTPException
import asyncpg

from backend.src.models.requests import UserSignup, UserLogin
from backend.src.models.responses import AuthResponse, UserInfoResponse, MessageResponse
from backend.src.services.auth_service import AuthService
from backend.src.services.chat_service import chat_service
from backend.src.core.dependencies import get_db_connection

router = APIRouter()
auth_service = AuthService()

@router.post("/signup", response_model=AuthResponse)
async def signup(user: UserSignup, conn: asyncpg.Connection = Depends(get_db_connection)):
    """Handle user signup"""
    student_id, session_token = await auth_service.create_user(
        conn, user.username, user.password, user.email
    )
    
    return AuthResponse(
        message="Signup successful",
        session_token=session_token,
        student_id=student_id
    )

@router.post("/login", response_model=AuthResponse)
async def login(user: UserLogin, conn: asyncpg.Connection = Depends(get_db_connection)):
    """Handle user login"""
    student_id, session_token = await auth_service.authenticate_user(
        conn, user.username, user.password
    )
    
    return AuthResponse(
        message="Login successful",
        session_token=session_token,
        student_id=student_id
    )

@router.post("/logout", response_model=MessageResponse)
async def logout(request: Request, conn: asyncpg.Connection = Depends(get_db_connection)):
    """Handle user logout"""
    session_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if not session_token:
        raise HTTPException(status_code=400, detail="No session token provided")
    
    student_id = await auth_service.logout_user(conn, session_token)
    
    # End chat session if active
    if student_id in chat_service.active_sessions:
        await chat_service.cleanup_session(student_id)
    
    return MessageResponse(message="Logout successful")

@router.get("/user-info", response_model=UserInfoResponse)
async def get_user_info(request: Request, conn: asyncpg.Connection = Depends(get_db_connection)):
    """Get user info for the current session"""
    session_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if not session_token:
        return UserInfoResponse(authenticated=False)
    
    user_info = await auth_service.get_user_from_token(conn, session_token)
    
    if user_info:
        username, student_id = user_info
        return UserInfoResponse(
            authenticated=True,
            username=username,
            student_id=student_id
        )
    else:
        return UserInfoResponse(authenticated=False)