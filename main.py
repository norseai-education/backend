from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import StreamingResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
import json
import logging
from typing import Optional, Dict, Any
import uuid
import hashlib
import secrets
import asyncpg
import os

from graph import BuildNorseAIGraph
from state_manager import StateManager
from database import MongoDBHandler
import utils

# Configure
logger = utils.set_logger(__name__)
load_dotenv()
db_pass = os.getenv('USER_DB_PASSWORD')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_pool

    try:
        db_pool = await asyncpg.create_pool(
            user='admin',
            password=db_pass,
            database='norseai',
            host='172.16.0.154',
            port=5432,
            min_size=1,
            max_size=30,
            timeout=20
    )
    except Exception as e:
        utils.log(f"Connection pool creation failed: {e}",logger,0)

    utils.log("User database pool connected", logger, 0)

    yield 

    # Shutdown 

    for student_id in list(active_sessions.keys()):
        await cleanup_session(student_id)

        try:
            async with db_pool.acquire() as conn:
                await conn.execute(
                    "DELETE FROM sessions WHERE student_id = $1",
                    student_id
                )
        except Exception as e:
            utils.log(f"Failed to delete session token for student {student_id}: {e}", logger, 0)
    if db_pool:
        await db_pool.close()
        utils.log("User database pool closed", logger, 0)



app = FastAPI(title="NorseAI Chat API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str
    student_id: int

class ChatResponse(BaseModel):
    response: str
    student_id: int

class UserSignup(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

# Global storage for active sessions and users
active_sessions: Dict[int, Dict[str, Any]] = {}

async def get_db_connection():
    async with db_pool.acquire() as conn:
        yield conn

async def initialize_student_session(student_id: int) -> Dict[str, Any]:
    """Initialize or retrieve student session with all components"""
    
    utils.log(f"Initializing new session for student {student_id}", logger, 1)
    
    # Initialize graph
    state_manager = StateManager(student_id)
    graph = BuildNorseAIGraph()
    graph_builder = graph.get_graph()
    norseai = state_manager.build_graph_redis(graph_builder)
    
    # Initialize MongoDB connection
    convo_db = MongoDBHandler("mongodb://172.16.0.177:27019")
    await asyncio.get_event_loop().run_in_executor(None, convo_db.connect, "norseai")
    
    # Load states
    persisted_state = await asyncio.get_event_loop().run_in_executor(None, state_manager.retrieve)
    redis_state = await asyncio.get_event_loop().run_in_executor(None, state_manager.get_redis_state)
    user_state = state_manager.default_state()
    
    utils.log(f"Mongo DB state: \n{persisted_state}\n", logger, 2)
    utils.log(f"Redis state : \n{redis_state}\n", logger, 2)
    
    # Apply persisted state
    if persisted_state:
        utils.log("Applying persisted state from MongoDB...", logger, 1)
        for key, value in persisted_state.items():
            if key in user_state:
                user_state[key] = value
        user_state['init_learning_objective'] = user_state['cur_learning_objective']
        utils.log("State from MongoDB applied!", logger, 1)
    
    # Apply Redis state
    if redis_state:
        utils.log("Applying Redis state...", logger, 1)
        for key, value in redis_state.items():
            if key in user_state:
                user_state[key] = value
        utils.log("State from Redis applied!", logger, 1)
    
    # Store session
    session_data = {
        'state_manager': state_manager,
        'norseai': norseai,
        'convo_db': convo_db,
        'user_state': user_state
    }
    
    active_sessions[student_id] = session_data

async def get_session(student_id: int):
    utils.log(f"Active sessions: {active_sessions}", logger, 2)
    if student_id in active_sessions:
        return active_sessions[student_id]

async def cleanup_session(student_id: int):
    """Clean up session resources"""
    if student_id in active_sessions:
        session = active_sessions[student_id]
        try:
            # Close database connection
            if 'convo_db' in session:
                session['convo_db'].close()
            utils.log(f"Session cleanup completed for student {student_id}", logger, 1)
        except Exception as e:
            utils.log(f"Error during session cleanup for student {student_id}: {e}", logger, 1)
        finally:
            # Remove from active sessions
            del active_sessions[student_id]

async def initialize(student_id: int):
    await initialize_student_session(student_id)

async def get_response(student_id: int, message: str):
    try:
        session = await get_session(student_id)
        state_manager = session['state_manager']
        norseai = session['norseai']
        convo_db = session['convo_db']
        user_state = session['user_state']
        
        # Manage conversation history length
        if len(user_state['messages']) > 60:
            old_messages = user_state["messages"][:-30]
            asyncio.create_task(
                convo_db.insert_document(
                    'conversation_history', 
                    utils.convert_messages_to_dict(old_messages, student_id),
                    True
                )
            )
            user_state["messages"] = user_state["messages"][-30:]
            utils.log(f"Trimmed conversation history for student {student_id}", logger, 1)
        
        # Check if lesson is complete
        if user_state.get("lesson_state", {}).get("END_LESSON", "").lower() == "done":
            # Store final state
            await asyncio.get_event_loop().run_in_executor(None, state_manager.store, user_state)
            await asyncio.get_event_loop().run_in_executor(None, state_manager.clear_redis_memory)
            
            # Store final conversation
            await convo_db.insert_document(
                "conversation_history",
                utils.convert_messages_to_dict(user_state["messages"]),
                True
            )
            
            yield f"data: {json.dumps({'type': 'lesson_complete', 'message': 'Lesson completed! State saved.'})}\n\n"
            await cleanup_session(student_id)
            return
        
        # Add user message to state
        user_state["messages"] = user_state.get("messages", []) + [
            {"role": "user", "content": message}
        ]
        
        # Send user message
        yield f"data: {json.dumps({'type': 'user_message', 'content': message})}\n\n"
        
        # Get response
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Processing...'})}\n\n"
        
        utils.log("Running the graph now...", logger, 1)
        utils.log(f"State before: \n{user_state}", logger, 1)
        # Run the graph in executor to avoid blocking
        user_state = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: norseai.invoke(user_state, {"configurable": {"thread_id": str(student_id)}})
        )
        
        # Update session state
        session['user_state'] = user_state

        utils.log(f"State after: \n{user_state}", logger, 1)
        
        # Extract and send AI response
        if "messages" in user_state and user_state["messages"]:
            last_message = user_state["messages"][-1]
            if hasattr(last_message, 'type') and last_message.type == 'ai':
                ai_response = last_message.content
                yield f"data: {json.dumps({'type': 'ai_response', 'content': ai_response})}\n\n"
            elif hasattr(last_message, 'role') and last_message.get('role') == 'assistant':
                ai_response = last_message.get('content', '')
                yield f"data: {json.dumps({'type': 'ai_response', 'content': ai_response})}\n\n"
        
        # Send completion signal
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
        
    except Exception as e:
        utils.log(f"Error processing message for student {student_id}: {str(e)}", logger, 2)
        yield f"data: {json.dumps({'type': 'error', 'message': f'An error occurred: {str(e)}'})}\n\n"

def hash_password(password: str) -> str:
    """Hash password with salt"""
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'salt', 100000).hex()

def generate_session_token() -> str:
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

@app.delete("/chat/session/{student_id}")
async def end_chat_session(student_id: int):
    """Manually end chat session"""
    if student_id in active_sessions:
        session = active_sessions[student_id]
        state_manager = session['state_manager']
        convo_db = session['convo_db']
        user_state = session['user_state']

        await convo_db.insert_document(
                "conversation_history",
                utils.convert_messages_to_dict(user_state["messages"]),
                True
            )
        utils.log("stored conversation history into database!", logger, 1)
        
        # Clear Redis memory
        await asyncio.get_event_loop().run_in_executor(None, state_manager.clear_redis_memory)
        await cleanup_session(student_id)
        
        return {"message": f"Session ended for student {student_id}"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/chat/status/{student_id}")
async def get_chat_status(student_id: int):
    """Get current student status"""
    if student_id in active_sessions:
        user_state = active_sessions[student_id]['user_state']
        return {
            "active": True,
            "message_count": len(user_state.get('messages', [])),
            "lesson_state": user_state.get('lesson_state', {}),
            "current_objective": user_state.get('cur_learning_objective', '')
        }
    else:
        return {"active": False}

@app.get("/")
async def home_page():
    try:
        with open("static/home.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Error</h1><p>Home page not found. Please ensure static/home.html exists.</p>",
            status_code=404
        )

@app.get("/login")
async def login_page():
    """login page"""
    try:
        with open("static/login.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Error</h1><p>Login page not found. Please ensure static/login.html exists.</p>",
            status_code=404
        )

@app.get("/signup")
async def signup_page():
    """signup page"""
    try:
        with open("static/signup.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Error</h1><p>Signup page not found. Please ensure static/signup.html exists.</p>",
            status_code=404
        )

@app.get("/chat")
async def chat_page():
    try:
        with open("static/chat.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Error</h1><p>Chat interface not found. Please ensure static/chat.html exists.</p>",
            status_code=404
        )

@app.get("/loading")
async def loading_page():
    """loading page"""
    try:
        with open("static/loading.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Error</h1><p>Loading page not found. Please ensure static/loading.html exists.</p>",
            status_code=404
        )

@app.get("/dashboard")
async def loading_page():
    """loading page"""
    try:
        with open("static/dashboard.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Error</h1><p>Loading page not found. Please ensure static/loading.html exists.</p>",
            status_code=404
        )

@app.get("/auth/user-info")
async def get_user_info(request: Request, conn: asyncpg.Connection = Depends(get_db_connection)):
    """Get user info for the current session"""
    session_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not session_token:
        return {"authenticated": False}
    
    # get student_id based on session_id
    student_id_result = await conn.fetchrow(
        "SELECT student_id FROM sessions WHERE session_token = $1",
        session_token
    )
    student_id = student_id_result["student_id"] if student_id_result else None

    if not student_id:
        return {"authenticated": False}
    
    # Find username by student_id
    username_result = await conn.fetchrow(
        "SELECT username FROM users WHERE student_id = $1",
        student_id
    )
    username = username_result["username"] if username_result else None
    
    if username:
        return {
            "authenticated": True,
            "username": username,
            "student_id": student_id
        }
    else:
        return {"authenticated": False}

@app.post("/chat/init/{student_id}")
async def init_chat(student_id: int):
    await initialize(student_id)
    return {"message": f"Student {student_id} initialized successfully"}

@app.post("/chat/s/{student_id}")
async def chat_stream(student_id: int, message_data: dict):
    message = message_data.get("message", "").strip()
    
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    async def event_generator():
        async for chunk in get_response(student_id, message):
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

@app.post("/auth/signup")
async def signup(user: UserSignup, conn: asyncpg.Connection = Depends(get_db_connection)):
    """Handle user signup"""

    username_result = await conn.fetchrow(
        "SELECT username FROM users WHERE username = $1",
        user.username
    )
    username = username_result['username'] if username_result else None

    if username:
        raise HTTPException(status_code=400, detail="Username already exists")

    utils.log("Username is valid and unique, creating student id...", logger, 1)
    next_student_id = await conn.fetchval(
        "SELECT COALESCE(MAX(student_id), 0) + 1 FROM users"
    )

    utils.log(f"Sucessfully got student id: {next_student_id}", logger, 1)

    # Store user
    await conn.execute(
        "INSERT INTO users (student_id, username, password, email) VALUES ($1, $2, $3, $4)",
        next_student_id, user.username, hash_password(user.password), user.email
    )

    utils.log(f"User logged in! student_id: {next_student_id}", logger, 1)

    # Create session and store
    session_token = generate_session_token()
    await conn.execute(
        "INSERT INTO sessions (student_id, session_token) VALUES ($1, $2)",
        next_student_id, session_token
    )
    
    return {
        "message": "Signup successful",
        "session_token": session_token,
        "student_id": next_student_id
    }

@app.post("/auth/login")
async def login(user: UserLogin, conn: asyncpg.Connection = Depends(get_db_connection)):
    """Handle user login"""

    # check username
    username_result = await conn.fetchrow(
        "SELECT username FROM users WHERE username = $1",
        user.username
    )
    username = username_result['username'] if username_result else None

    if not username:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # check password
    password_result = await conn.fetchrow(
        "SELECT password FROM users WHERE username = $1",
        user.username
    )
    password = password_result["password"]

    if password != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Get student id
    student_id_result = await conn.fetchrow(
        "SELECT student_id from USERS WHERE username = $1 AND password = $2",
        user.username,
        hash_password(user.password)
    )
    student_id = student_id_result["student_id"]

    # Create session (replace existing)
    session_token = generate_session_token()
    # Update session
    await conn.execute(
        "INSERT INTO sessions (student_id, session_token) VALUES ($1, $2)",
        student_id, session_token
    )

    utils.log(f"User logged in! student_id: {student_id}", logger, 1)
    
    return {
        "message": "Login successful",
        "session_token": session_token,
        "student_id": student_id
    }

@app.post("/auth/logout")
async def logout(session_token: str, conn: asyncpg.Connection = Depends(get_db_connection)):
    """Handle user logout"""

    student_id_result = await conn.fetchrow(
        "SELECT student_id from sessions WHERE session_token = $1",
        session_token
    )
    student_id = student_id_result["student_id"] if student_id_result else None

    if not student_id:
        raise HTTPException(status_code=404, detail="Student ID not found")
    

    utils.log(f"Removing user with student_id: {student_id}", logger, 1)
    
    # End chat session if active
    if student_id in active_sessions:
        await cleanup_session(student_id)
    
    # Remove session
    await conn.execute(
        "DELETE FROM sessions WHERE student_id = $1",
        student_id
    )
    
    return {"message": "Logout successful"}
        

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")