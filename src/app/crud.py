from fastapi import HTTPException, status
from typing import (
    List,
    Dict,
    Any
)

from core.config import settings

from core.security.utils import Hash
from core.schemas.user import (
    UserCreate,
    UserDB,
    ROLE
)
from core.schemas.grade import GradeDB

async def get_user_by_username(*, username: int | str) -> dict | None:
    """
    Find user by username. e.g `edbo_id` or `email` 
    """
    collections = await UserDB.get_collections()
    for collection in collections:
        UserDB.COLLECTION_NAME = collection
        user = await UserDB.find_by(
            {"edbo_id": int(username)} if username.isdigit() else {"email": username})
        if user: break 
    return user

async def create_user(*, user: UserCreate) -> bool:
    """
    Create a new user in the MongoDB collection.
    """
    if await UserDB.find_by({"edbo_id": user.edbo_id}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exits."
        )
    UserDB.COLLECTION_NAME = user.role
    user.password = Hash.hash(plain=user.password)
    await UserDB.create(doc=user.model_dump())
    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="User created successfully."
    )

async def read_users(*, role: ROLE, filter: str | None = None, value: Any, skip: int = 0, length: int | None = None) -> List[Dict[str, Any]]:
    """
    Read all users from the MongoDB collection.
    """
    UserDB.COLLECTION_NAME = role
    return await UserDB.find_many(
        filter=filter, value=value, skip=skip, length=length)

async def read_user(*, edbo_id: int) -> Dict[str, Any]:
    """
    Read user from the MongoDB collection.
    """
    user = await get_user_by_username(username=edbo_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return user 

async def update_all_users(*, collection: ROLE, filter: dict, update: dict):
    """
    Update users data.
    """
    UserDB.COLLECTION_NAME = collection
    await UserDB.update_many(
        filter=filter,
        update=update)
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="User accounts has been updated.")

async def update_user(*, edbo_id: int, data: dict):
    """
    Update user data.
    """
    user = await get_user_by_username(username=edbo_id)
    if not user:
       raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        ) 
    await UserDB.update_one(
        filter={"edbo_id": user.get("edbo_id")},
        update=data)
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="The user account has been updated.")

async def delete_user(*, user: dict):
    """
    Delete user from the MongoDB collection by `edbo_id`.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    await UserDB.delete_document_by({"edbo_id": user.get("edbo_id")})
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="The user account has been deleted")

async def authenticate_user(*, username: str | int, plain_pwd: str, exclude: List[str] | None = None) -> dict:
    """
    Authenticate user credentials.
    """
    user = await get_user_by_username(username=username)
    if not user or not Hash.verify(plain_pwd, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Couldn't validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    # Check user scopes (privileges)
    scopes = user.get("scopes")
    for scope in scopes:
        if scope not in settings.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user credentials."
            )
    if exclude:
        for key in exclude:
            user.pop(key)
    return user

async def get_grades(*, edbo_id: int, group: str, **kwargs) -> dict:
    """
    Get student subject grades.
    """
    GradeDB.COLLECTION_NAME = group
    grades: dict = await GradeDB.find_by({"edbo_id": edbo_id})
    if grades:
        disciplines: dict = grades.get("disciplines")  
        subject, date = kwargs.get("subject"), kwargs.get("date")
        if subject:
            grades: dict = disciplines.get(subject, {})
            if date:
                grades = grades.get(date, None)
        else:
            grades = {}
            for subject, value in disciplines.items():
                grades.update({subject: value.get(date) if date else value})
    return grades