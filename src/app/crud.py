from core.security.utils import Hash
from core.schemas.user import (
    UserCreate,
    UserDelete,
    UserDB,
)
from core import exc
from typing import (
    List,
    Dict,
    Any
)

async def get_user_by_username(*, username: str) -> dict | None:
    """
        Find user by username. e.g 'edbo_id' or 'email' 
    """
    collections = await UserDB.get_collections()
    for collection in collections:
        UserDB.COLLECTION_NAME = collection
        user = await UserDB.find_by({"email": str(username)})
        if not user:
            try:
                user = await UserDB.find_by({"edbo_id": int(username)})
            except:
                continue
        if user:
            break
    return user

async def create_user(*, user: UserCreate) -> bool:
    """
        Create a new user in the MongoDB collection.
    """
    if await UserDB.find_by({"edbo_id": user.edbo_id}):
        raise exc.UNPROCESSABLE_CONTENT(detail="User already exits.")
    user.password = Hash.hash(user.password)
    await UserDB.create(user.model_dump())
    raise exc.CREATED(detail="User created successfully.")

async def read_users(*, collection: str, skip: int = 0, length: int | None = None) -> List[Dict[str, Any]]:
    """
        Read all users from the MongoDB collection.
    """
    collections = await UserDB.get_collections()
    if collection not in collections:
        raise exc.NOT_FOUND(
            detail=f"The collection '{collection}' not found.")
    UserDB.COLLECTION_NAME = collection
    return await UserDB.find_all(skip=skip, length=length)

async def read_user(*, username: str) -> Dict[str, Any]:
    """
        Read user from the MongoDB collection.
    """
    user = get_user_by_username(username=username)
    if not user:
        raise exc.NOT_FOUND(detail="User not found")
    return user 

async def delete_user(*, user: UserDelete):
    """
        Delete user from the MongoDB collection by edbo_id.
    """
    user = await UserDB.find_by({"edbo_id": user.edbo_id})
    if not user:
        raise exc.UNPROCESSABLE_CONTENT()
    await UserDB.delete_document_by({"edbo_id": user.edbo_id})
    raise exc.OK()

async def authenticate_user(*, username: str | int, plain_pwd: str) -> Dict[str, Any] | bool:
    """
        Authenticate user credentials.
    """
    user = await get_user_by_username(username=username)
    if not user or not Hash.verify(plain_pwd, user["password"]):
        raise exc.UNAUTHORIZED(
            detail="Couldn't validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user