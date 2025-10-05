from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment based on APP_ENV variable
app_env = os.getenv('APP_ENV', 'dev')
if app_env == 'prod':
    load_dotenv('.env.prod')
else:
    load_dotenv('.env.dev')

class Settings(BaseSettings):
    # Server network configuration
    server_network: str = os.getenv('SERVER_NETWORK', '172.16.0.154')
    
    # Database settings
    db_user: str = "admin"
    db_password: str = os.getenv('USER_DB_PASSWORD', 'defaultpassword')
    db_name: str = "norseai"
    db_host: str = os.getenv('DB_HOST', 'postgres')
    db_port: int = 5432
    db_min_pool_size: int = 1
    db_max_pool_size: int = 30
    db_timeout: int = 20
    
    # MongoDB settings - use environment-specific URLs
    mongodb_url: str = os.getenv('DEV_MONGODB_URL', 'mongodb://mongodb:27017')
    if app_env == 'prod':
        mongodb_url = os.getenv('PROD_MONGODB_URL', 'mongodb://mongodb:27017')
    
    mongodb_database: str = "amc8_database"
    
    # Redis settings
    redis_url: str = os.getenv('REDIS_URL', 'redis://redis:6379/') 
    
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