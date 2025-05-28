from datetime import datetime, timedelta, timezone
from redis.asyncio import Redis
from typing import Optional
import jwt

from core.logger import logger
from core.config import settings

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
    def decode(token: str) -> Optional[str]:
        """
        Decodes a JWT, returning the payload.
        """
        try:
            return jwt.decode(jwt=token, key=settings.PUBLIC_KEY_PEM, algorithms=settings.JWT_ALGORITHM)
        except jwt.DecodeError:
            return None

    @staticmethod
    async def refresh(payload: dict) -> str:
        """
        Refreshes the claims of a JWT, updating expiry time.
        """
        payload.update(
            {"exp": datetime.now(tz=timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MIN)})
        return jwt.encode(payload=payload, key=settings.PRIVATE_KEY_PEM, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    async def add_jwt_to_blacklist(jti: str, exp: int, redis: Redis) -> bool:
        """
        Adds `jwt` to the blacklist. 
        """
        try:
            now = int(datetime.now(tz=timezone.utc).timestamp())
            ttl = exp - now
            if ttl < 0:
                logger.warning(f"Token with jti={jti} is already expired. Skipping blacklist.")
                return False
            
            # store blacklist entry
            await redis.setex(f"oauth:blacklist:{jti}", ttl, "Revoked")
            return True
        except Exception as err:
            logger.error({
                "msg": f"Failed to add token to blacklist.",
                "detail": err
            })
            return False

    @staticmethod
    async def is_jwt_in_blacklist(jti: str, redis: Redis) -> bool:
        """
        Checks if the `jwt` is in blacklist.
        """
        return await redis.exists(f"oauth:blacklist:{jti}")