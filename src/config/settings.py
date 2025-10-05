from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database postgresql settings
    db_user: str = "admin"
    db_password: str = Field(default="", alias="USER_DB_PASSWORD")
    db_name: str = "norseai"
    db_host: str = Field(default="172.16.0.154", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_min_pool_size: int = 1
    db_max_pool_size: int = 30
    db_timeout: int = 20
    
    # MongoDB settings
    mongodb_host: str = Field(default="172.16.0.177", env="MONGODB_HOST")
    mongodb_port: int = Field(default=27019, env="MONGODB_PORT")
    mongodb_database: str = "amc8_database"
    
    @property
    def mongodb_url(self) -> str:
        return f"mongodb://{self.mongodb_host}:{self.mongodb_port}"
    
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