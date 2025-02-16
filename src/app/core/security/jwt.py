from datetime import datetime, timedelta, timezone
import jwt

from core.config import settings
from core.logger import logger

from core.schemas.user import UserDB
from core.schemas.etc import Token
from core import exc

# https://www.iana.org/assignments/jwt/jwt.xhtml#claims

class OAuthJWTBearer:
    """
        JSON Web Token (JWT) is a compact, URL-safe means of representing
        claims to be transferred between two parties.
    """

    @staticmethod
    def encode(payload: dict) -> str:
        payload.update(
            {"exp": datetime.now(tz=timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MIN),
            "iat": datetime.now(tz=timezone.utc)})
        return jwt.encode(payload=payload, key=settings.PRIVATE_KEY_PEM, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def decode(token: str) -> dict:
        try:
            return jwt.decode(jwt=token, key=settings.PUBLIC_KEY_PEM, algorithms=settings.JWT_ALGORITHM)
        except jwt.DecodeError as err:
            logger.error(err)
            raise exc.UNAUTHORIZED(
                detail="Couldn't validate user credentials",
                headers={"WWW-Authenticate": "Bearer"})
     
    @staticmethod
    def refresh(payload: dict) -> str:
        payload.update(
            {"exp": datetime.now(tz=timezone.utc) + timedelta(minutes=settings.JWT_REFRESH_MIN)})
        return jwt.encode(payload=payload, key=settings.PRIVATE_KEY_PEM, algorithm=settings.JWT_ALGORITHM)

    @classmethod
    async def verify(cls, token: str) -> Token:
        payload: dict = cls.decode(token=token)
        edbo_id = int(payload.get("sub"))
        user = await UserDB.find_by({"edbo_id": edbo_id})
        if not user:
            exc.UNAUTHORIZED(
                detail="Couldn't validate user credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        token = cls.refresh(payload=payload)
        return Token(access_token=token)