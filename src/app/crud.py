from core.security.utils import get_hash_pwd, verify_pwd
from core import exceptions
from core.schemas.user import (
    UserCreate,
    UserDB
)
from typing import (
    List,
    Dict,
    Any
)

async def create_user(*, user_create: UserCreate) -> bool:
    """Create a new user in the MongoDB collection."""
    user = await UserDB.find_by({"edbo_id": user_create.edbo_id})
    if user:
        raise exceptions.UNPROCESSABLE_CONTENT(detail="User already exits.")
    user_create.password = get_hash_pwd(user_create.password)
    await UserDB.create(user_create.model_dump())
    raise exceptions.CREATED(detail="User created successfully.")

async def read_users(*, skip: int = 0, length: int | None = None) -> List[Dict[str, Any]]:
    """Read all users from the MongoDB collection."""
    return await UserDB.find_all(skip=skip, length=length)

async def read_user(*, edbo_id: int) -> Dict[str, Any]:
    """Read user from the MongoDB collection."""
    user = await UserDB.find_by({"edbo_id": edbo_id})
    if not user:
        raise exceptions.NOT_FOUND()
    return user 

async def delete_user(*, edbo_id: int):
    """Delete user from the MongoDB collection by edbo_id."""
    user = await UserDB.find_by({"edbo_id": edbo_id})
    if not user:
        raise exceptions.UNPROCESSABLE_CONTENT()
    await UserDB.delete_doc_by({"edbo_id": edbo_id})
    raise exceptions.OK()

async def authenticate_user(*, edbo_id: int, plain_pwd: str) -> Dict[str, Any] | bool:
    """Authenticate / verify user"""
    user = await UserDB.find_by({"edbo_id": edbo_id})
    if not user:
        return False
    if not verify_pwd(plain_pwd, user["password"]):
        return False
    return user