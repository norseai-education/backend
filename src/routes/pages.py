from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home_page():
    """Home page"""
    try:
        with open("backend/static/home.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Error</h1><p>Home page not found. Please ensure static/home.html exists.</p>",
            status_code=404
        )

@router.get("/login", response_class=HTMLResponse)
async def login_page():
    """Login page"""
    try:
        with open("backend/static/login.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Error</h1><p>Login page not found. Please ensure static/login.html exists.</p>",
            status_code=404
        )

@router.get("/signup", response_class=HTMLResponse)
async def signup_page():
    """Signup page"""
    try:
        with open("backend/static/signup.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Error</h1><p>Signup page not found. Please ensure static/signup.html exists.</p>",
            status_code=404
        )

@router.get("/chat", response_class=HTMLResponse)
async def chat_page():
    """Chat interface"""
    try:
        with open("backend/static/chat.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Error</h1><p>Chat interface not found. Please ensure static/chat.html exists.</p>",
            status_code=404
        )

@router.get("/loading", response_class=HTMLResponse)
async def loading_page():
    """Loading page"""
    try:
        with open("backend/static/loading.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Error</h1><p>Loading page not found. Please ensure static/loading.html exists.</p>",
            status_code=404
        )

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """Dashboard page"""
    try:
        with open("backend/static/dashboard.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Error</h1><p>Dashboard page not found. Please ensure static/dashboard.html exists.</p>",
            status_code=404
        )
    

@router.get("/assessment", response_class=HTMLResponse)
async def assessment_page():
    """Assessment page"""
    try:
        with open("backend/static/assessment.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Error</h1><p>Assessment page not found. Please ensure static/assessment.html exists.</p>",
            status_code=404
        )