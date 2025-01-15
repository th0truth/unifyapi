from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from typing import Dict, Any
import jwt

from core.config import settings

def encode_token(
        payload: Dict[str, Any],
        private_key: str | bytes = settings.PRIVATE_KEY_PEM,
        algorithm: str = settings.JWT_ALGORITHM
) -> str:
    # NOTE: https://www.iana.org/assignments/jwt/jwt.xhtml#claims
    payload.update(
        {"exp": datetime.now(tz=timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MIN),
         "iat": datetime.now(tz=timezone.utc)})
    return jwt.encode(payload=payload, key=private_key, algorithm=algorithm)

def decode_token(
        token: str | bytes,
        public_key: str | bytes = settings.PUBLIC_KEY_PEM,
        algorithms: list[str] = settings.JWT_ALGORITHM
) -> dict:
    try:
        # https://auth0.com/blog/how-to-handle-jwt-in-python/ |
        return jwt.decode(jwt=token, key=public_key, algorithms=algorithms)
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Couldn't validate credentials",
                headers={"WWW-Authenticate": "Bearer"})