from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from typing import Dict, Any
import secrets

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

class Settings(BaseSettings): 
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore"
    )
    
    # ENVIRONMENT: Literal["local", "production"] = "local"
 
    # API settings
    
    NAME: str
    DESCRIPTION: str = ""
    SUMMARY: str | None = None
    VERSION: str = "0.0.1"
    API_V1_STR: str = "/api/v1"

    # Database (MongoDB) settings    
    
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOSTNAME: str
    
    # Authorization

    JWT_ALGORITHM: str = "RS256"
    JWT_EXPIRE_MIN: int | float
    JWT_REFRESH_MIN: int | float

    scopes: Dict[str, Any] = {
        "student": "",
        "lecturer": "",
        "admin": ""
    }

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    REDIRECT_URL: str
    SECRET_KEY: str = secrets.token_hex(32)

    PRIVATE_KEY_PEM: bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption())
    
    PUBLIC_KEY_PEM: bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)
    
settings = Settings()