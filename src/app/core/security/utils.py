from passlib.context import CryptContext
from passlib import exc

from core.logger import logger

class Hash:
    context = CryptContext(schemes=["argon2"], deprecated="auto")

    @classmethod
    def hash(cls, plain: str) -> str:
        """Return hashed password."""
        try:
            return cls.context.hash(secret=plain)
        except exc.PasswordValueError as err:
            logger.error(err)

    @classmethod
    def verify(cls, plain: str, hashed: str) -> bool:
        """Return bool type of the verified password"""
        try:
            return cls.context.verify(secret=plain, hash=hashed)
        except exc.PasswordValueError as err:
            logger.error(err)