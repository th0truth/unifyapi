from passlib.context import CryptContext

class Hash:
    """
        Hashing algorithms.

        docs: https://passlib.readthedocs.io/en/stable/index.html
    """
    context = CryptContext(schemes=["argon2"], deprecated="auto")

    @classmethod
    def hash(cls, plain_pwd: str | bytes) -> str:
        return cls.context.hash(secret=plain_pwd)
        
    @classmethod
    def verify(cls, plain_pwd: str | bytes, hashed_pwd: str | bytes) -> bool:
        try:
            return cls.context.verify(secret=plain_pwd, hash=hashed_pwd)
        except:
            return False