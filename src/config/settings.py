from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database postgresql settings
    db_user: str = "admin"
    db_password: str = os.getenv('USER_DB_PASSWORD', '')
    db_name: str = "norseai"
    db_host: str = "172.16.0.154"
    db_port: int = 5432
    db_min_pool_size: int = 1
    db_max_pool_size: int = 30
    db_timeout: int = 20
    
    # MongoDB settings
    mongodb_url: str = "mongodb://172.16.0.177:27019"
    mongodb_database: str = "amc8_database"
    
    # Security settings
    password_salt: bytes = b'salt'
    password_iterations: int = 100000
    
    # Session settings
    max_conversation_length: int = 60
    conversation_keep_recent: int = 30
    
    # CORS settings
    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()