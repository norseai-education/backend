from fastapi import Depends, Request
import asyncpg

async def get_db_connection(request: Request):
    """Get database connection from pool"""
    async with request.app.state.db_pool.acquire() as conn:
        yield conn