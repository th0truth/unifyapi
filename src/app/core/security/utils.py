from passlib.context import CryptContext
from core.schemas import user

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_hash_pwd(plain_pwd: str | bytes) -> str:
    return pwd_context.hash(secret=plain_pwd)

def verify_pwd(plain_pwd: str | bytes, hashed_pwd: str | bytes) -> bool:
    try: return pwd_context.verify(secret=plain_pwd, hash=hashed_pwd)
    except:
        return False