from datetime import datetime, timedelta, timezone
from core.schemas.user import UserDB
from core.schemas.utils import Token
from core import exc
import jwt

from core.config import settings
from core.logger import logger

# https://www.iana.org/assignments/jwt/jwt.xhtml#claims

class OAuthJWTBearer:
    """
        JSON Web Token (JWT) is a compact, URL-safe means of representing
        claims to be transferred between two parties.
        
        docs:
            https://auth0.com/blog/how-to-handle-jwt-in-python/ 
    """
    algorithm: str = settings.JWT_ALGORITHM
    private_key: str | bytes = settings.PRIVATE_KEY_PEM
    public_key: str | bytes = settings.PUBLIC_KEY_PEM

    @classmethod
    def encode(cls, payload: dict) -> str:
        payload.update(
            {"exp": datetime.now(tz=timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MIN),
            "iat": datetime.now(tz=timezone.utc)})
        return jwt.encode(payload=payload, key=cls.private_key, algorithm=cls.algorithm)
    
    @classmethod
    def decode(cls, token: str) -> dict:
        try:
            return jwt.decode(jwt=token, key=cls.public_key, algorithms=cls.algorithm)
        except jwt.DecodeError as err:
            logger.error(err)
            raise exc.UNAUTHORIZED(
                detail="Couldn't validate user credentials",
                headers={"WWW-Authenticate": "Bearer"})
     
    @classmethod
    def refresh(cls, payload: dict) -> str:
        payload.update(
            {"exp": datetime.now(tz=timezone.utc) + timedelta(minutes=settings.JWT_REFRESH_MIN)})
        return jwt.encode(payload=payload, key=cls.private_key, algorithm=cls.algorithm)

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