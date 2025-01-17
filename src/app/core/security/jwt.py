from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from core import exceptions
import jwt

from core.config import settings

# https://www.iana.org/assignments/jwt/jwt.xhtml#claims
# https://auth0.com/blog/how-to-handle-jwt-in-python/ |

def encode_token(
    payload: Dict[str, Any],
    private_key: str | bytes = settings.PRIVATE_KEY_PEM,
    algorithm: str = settings.JWT_ALGORITHM
) -> str:
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
        return jwt.decode(jwt=token, key=public_key, algorithms=algorithms)
    except jwt.DecodeError:
        raise exceptions.UNAUTHORIZED(
            detail="Couldn't validate credentials",
            headers={"WWW-Authenticate": "Bearer"})
    
def refresh_token(payload: dict) -> str:
    payload.update(
        {"exp": datetime.now(tz=timezone.utc) + timedelta(minutes=settings.JWT_RERESH_MIN)})
    return encode_token(payload=payload)