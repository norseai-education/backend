import hashlib
import secrets
from src.config.settings import settings

def hash_password(password: str) -> str:
    """Hash password with salt"""
    return hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        settings.password_salt, 
        settings.password_iterations
    ).hex()

def generate_session_token() -> str:
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed_password