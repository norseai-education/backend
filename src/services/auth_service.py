import hashlib
import secrets
from typing import Optional
import asyncpg
from fastapi import HTTPException

from backend.src.config.settings import settings
from backend.src.utils import logging, security

class AuthService:
    def __init__(self):
        self.logger = logging.set_logger(__name__)
    
    async def create_user(self, conn: asyncpg.Connection, username: str, password: str, email: Optional[str] = None) -> tuple[int, str]:
        """Create new user and return student_id and session_token"""
        
        # Check if username exists
        username_result = await conn.fetchrow(
            "SELECT username FROM users WHERE username = $1",
            username
        )
        
        if username_result:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        logging.log("Username is valid and unique, creating student id...", self.logger, 1)
        
        # Get next student ID
        next_student_id = await conn.fetchval(
            "SELECT COALESCE(MAX(student_id), 0) + 1 FROM users"
        )
        
        logging.log(f"Successfully got student id: {next_student_id}", self.logger, 1)
        
        # Store user
        await conn.execute(
            "INSERT INTO users (student_id, username, password, email) VALUES ($1, $2, $3, $4)",
            next_student_id, username, security.hash_password(password), email
        )
        
        # Create session
        session_token = security.generate_session_token()
        await conn.execute(
            "INSERT INTO sessions (student_id, session_token) VALUES ($1, $2)",
            next_student_id, session_token
        )
        
        logging.log(f"User created! student_id: {next_student_id}", self.logger, 1)
        
        return next_student_id, session_token
    
    async def authenticate_user(self, conn: asyncpg.Connection, username: str, password: str) -> tuple[int, str]:
        """Authenticate user and return student_id and session_token"""
        
        # Check username exists
        username_result = await conn.fetchrow(
            "SELECT username FROM users WHERE username = $1",
            username
        )
        
        if not username_result:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Check password
        password_result = await conn.fetchrow(
            "SELECT password FROM users WHERE username = $1",
            username
        )
        
        if password_result["password"] != security.hash_password(password):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Get student ID
        student_id_result = await conn.fetchrow(
            "SELECT student_id FROM users WHERE username = $1 AND password = $2",
            username,
            security.hash_password(password)
        )
        student_id = student_id_result["student_id"]
        
        # Create new session
        session_token = security.generate_session_token()
        await conn.execute(
            "INSERT INTO sessions (student_id, session_token) VALUES ($1, $2)",
            student_id, session_token
        )
        
        logging.log(f"User logged in! student_id: {student_id}", self.logger, 1)
        
        return student_id, session_token
    
    async def get_user_from_token(self, conn: asyncpg.Connection, session_token: str) -> Optional[tuple[str, int]]:
        """Get username and student_id from session token"""
        
        # Get student_id from session
        student_id_result = await conn.fetchrow(
            "SELECT student_id FROM sessions WHERE session_token = $1",
            session_token
        )
        
        if not student_id_result:
            return None
        
        student_id = student_id_result["student_id"]
        
        # Get username
        username_result = await conn.fetchrow(
            "SELECT username FROM users WHERE student_id = $1",
            student_id
        )
        
        if not username_result:
            return None
        
        return username_result["username"], student_id
    
    async def logout_user(self, conn: asyncpg.Connection, session_token: str) -> int:
        """Logout user and return student_id"""
        
        student_id_result = await conn.fetchrow(
            "SELECT student_id FROM sessions WHERE session_token = $1",
            session_token
        )
        
        if not student_id_result:
            raise HTTPException(status_code=404, detail="Student ID not found")
        
        student_id = student_id_result["student_id"]
        
        # Remove session
        await conn.execute(
            "DELETE FROM sessions WHERE student_id = $1",
            student_id
        )
        
        logging.log(f"User logged out! student_id: {student_id}", self.logger, 1)
        
        return student_id