from core.security.utils import get_hash_pwd, verify_pwd
from core.security.jwt import OAuthJWTBearer
from core.schemas.user import (
    UserCreate,
    UserDelete,
    UserDB
)
from core import exceptions
from typing import (
    List,
    Dict,
    Any
)

async def create_user(*, user: UserCreate) -> bool:
    """Create a new user in the MongoDB collection."""
    UserDB.DATABASE_NAME = user.role
    if await UserDB.find_by({"edbo_id": user.edbo_id}):
        raise exceptions.UNPROCESSABLE_CONTENT(detail="User already exits.")
    user.password = get_hash_pwd(user.password)
    await UserDB.create(user.model_dump())
    raise exceptions.CREATED(detail="User created successfully.")

async def read_users(*, skip: int = 0, length: int | None = None) -> List[Dict[str, Any]]:
    """Read all users from the MongoDB collection."""
    return await UserDB.find_all(skip=skip, length=length)

async def read_user(*, edbo_id: int) -> Dict[str, Any]:
    """Read user from the MongoDB collection."""
    user = await UserDB.find_by({"edbo_id": edbo_id})
    if not user:
        raise exceptions.NOT_FOUND(detail="User not found")
    return user 

async def delete_user(*, user: UserDelete):
    """Delete user from the MongoDB collection by edbo_id."""
    UserDB.DATABASE_NAME = user.role
    user = await UserDB.find_by({"edbo_id": user.edbo_id})
    if not user:
        raise exceptions.UNPROCESSABLE_CONTENT()
    await UserDB.delete_doc_by({"edbo_id": user.edbo_id})
    raise exceptions.OK()

async def authenticate_user(*, edbo_id: int, plain_pwd: str) -> Dict[str, Any] | bool:
    """Authenticate / verify user"""
    user = await UserDB.find_by({"edbo_id": edbo_id})
    if not user or not verify_pwd(plain_pwd, user["password"]):
        raise exceptions.UNAUTHORIZED(
            detail="Couldn't validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

async def verify_user_token(*, token: str) -> bool:
    edbo_id = OAuthJWTBearer.decode(token=token).get("sub")
    user = await UserDB.find_by({"edbo_id": int(edbo_id)})
    if not user:
        raise exceptions.UNAUTHORIZED(
            detail="Couldn't validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    # return bool