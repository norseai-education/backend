from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncpg

from src.config.settings import settings
from src.services.chat_service import ChatService
from src.utils import logging

# Global database pool
db_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global db_pool
    
    # Startup
    logger = logging.set_logger(__name__)
    
    try:
        db_pool = await asyncpg.create_pool(
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            host=settings.db_host,
            port=settings.db_port,
            min_size=settings.db_min_pool_size,
            max_size=settings.db_max_pool_size,
            timeout=settings.db_timeout
        )
        logging.log("User database pool connected", logger, 0)
    except Exception as e:
        logging.log(f"Connection pool creation failed: {e}", logger, 0)
        raise
    
    # Store pool in app state
    app.state.db_pool = db_pool
    
    yield
    
    # Shutdown
    chat_service = ChatService()
    await chat_service.cleanup_all_sessions()
    
    if db_pool:
        await db_pool.close()
        logging.log("User database pool closed", logger, 0)