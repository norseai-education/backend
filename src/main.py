from fastapi import FastAPI

from src.core.lifespan import lifespan
from src.core.middleware import setup_middleware
from src.routes import auth, chat, assessment, classes, user_graph, user, evaluator_store

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
    app.include_router(assessment.router, prefix="/assessment", tags=["assessment"])
    app.include_router(classes.router, prefix="/classes", tags=["classes"])
    app.include_router(user_graph.router, prefix="/user_graph", tags=["user_graph"])
    app.include_router(user.router, prefix="/user", tags=["user"])
    app.include_router(evaluator_store.router, prefix="/evaluator_store", tags=["evaluator_store"])
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6700, log_level="info")