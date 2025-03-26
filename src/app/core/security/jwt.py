from datetime import datetime, timedelta, timezone
import jwt

from core.config import settings
from core.logger import logger
from core.db import Redis

# https://www.iana.org/assignments/jwt/jwt.xhtml#claims

class OAuthJWTBearer:
    """
        JSON Web Token (JWT) is a compact, URL-safe means of representing
        claims to be transferred between two parties.
    """

    @staticmethod
    def encode(payload: dict) -> str:
        """
        Encodes a given payload into a JWT.
        """
        payload.update(
            {"exp": datetime.now(tz=timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MIN),
            "iat": datetime.now(tz=timezone.utc)})
        return jwt.encode(payload=payload, key=settings.PRIVATE_KEY_PEM, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def decode(token: str) -> dict | None:
        """
        Decodes a JWT, returning the payload.
        """
        try:
            return jwt.decode(jwt=token, key=settings.PUBLIC_KEY_PEM, algorithms=settings.JWT_ALGORITHM)
        except jwt.DecodeError as err:
            logger.error(err)
     
    @staticmethod
    def refresh(payload: dict) -> str:
        """
        Refreshes the claims of a JWT, updating expiry time.
        """
        payload.update(
            {"exp": datetime.now(tz=timezone.utc) + timedelta(minutes=settings.JWT_REFRESH_MIN)})
        return jwt.encode(payload=payload, key=settings.PRIVATE_KEY_PEM, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    async def add_jti_to_blacklist(jti: str) -> bool:
        async with Redis(db=0) as client:
            response = await client.set(name=jti, value="", ex=settings.JTI_EXPIRY_SEC)
            return response
        
    @staticmethod
    async def is_jti_in_blacklist(jti: str) -> bool:
        async with Redis(db=0) as client:
            response = await client.exists(jti)
            return response