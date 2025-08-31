from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.config.settings import settings

def setup_middleware(app: FastAPI):
    """Setup application middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )