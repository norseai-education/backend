from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.src.core.lifespan import lifespan
from backend.src.core.middleware import setup_middleware
from backend.src.routes import auth, chat, pages

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="NorseAI Chat API", 
        version="1.0.0", 
        lifespan=lifespan
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Include routers
    app.include_router(auth.router, prefix="/auth", tags=["authentication"])
    app.include_router(chat.router, prefix="/chat", tags=["chat"])
    app.include_router(pages.router, tags=["pages"])
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")