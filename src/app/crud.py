from pymongo.asynchronous.database import AsyncDatabase
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Any

from core.config import settings
from core.security.utils import Hash
from core.schemas.user import (
    UserBase,
    UserCreate,
)
      
async def get_user_by_username(
        db: AsyncDatabase,
        *,
        username: int | str,
        exclude: Optional[list] = None
    ) -> dict:
    """
    Find user by `username`. 
    """
    for name in await db.list_collection_names():
        collection = db.get_collection(name)
        user = await collection.find_one(
            {"edbo_id": int(username)} if isinstance(username, int) or username.isdigit() else {"email": username}) 
        if user: break
    if exclude:
      for key in exclude:
        user.pop(key)
    return user

async def create_user(
        db: AsyncDatabase,
        *,
        user: UserCreate
    ) -> bool:
    """
    Create a new user in the MongoDB collection.
    """
    
    if await get_user_by_username(db, username=user.edbo_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exits."
        )
    collection = db.get_collection(user.role)
    user.password = Hash.hash(plain=user.password)
    await collection.insert_one(user.model_dump())
    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="User created successfully."
    )

async def read_users(
        db: AsyncDatabase,
        *,
        role: str,
        filter: Any,
        value: Any,
    ) -> List[UserBase]:
    """
    Read all users.
    """
    collection = db.get_collection(role)
    return await collection.find({filter: value} if filter and value else {}).to_list()
    
async def read_user(
        db: AsyncDatabase, 
        *,
        edbo_id: int
    ) -> Dict[str, Any]:
    """
    Read user from the MongoDB collection.
    """
    user = await get_user_by_username(db, username=edbo_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return user 

async def update_all_users(
        db: AsyncDatabase,
        *,
        role: str,
        update_doc: dict
    ):
    """
    Update users data.
    """
    collection = db.get_collection(role)
    await collection.update_many({}, update={"$set": update_doc})
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="User accounts has been updated."
    )

async def update_user(
        db: AsyncDatabase,
        *,
        edbo_id: int,
        update_doc: dict
    ):
    """
    Update user data.
    """
    user = await get_user_by_username(db, username=edbo_id)
    if not user:
       raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        ) 
    collection = db.get_collection(user.get("role"))
    await collection.update_one(
        filter={"edbo_id": edbo_id},
        update={"$set": update_doc}
    )
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="The user account has been updated."
    )

async def delete_user(
        db: AsyncDatabase,
        *,
        edbo_id: int
    ):
    """
    Delete user from the MongoDB collection by `edbo_id`.
    """
    user = await get_user_by_username(db, username=edbo_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    collection = db.get_collection(user.get("role"))
    d = await collection.delete_one({"edbo_id": edbo_id})
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="The user account has been deleted"
    )

async def authenticate_user(
        db: AsyncDatabase,
        *,
        username: str | int,
        plain_pwd: str,
        exclude: Optional[list] = None
    ) -> dict:
    """
    Authenticate user credentials.
    """ 
    user = await get_user_by_username(db, username=username)
    if not user or not Hash.verify(plain_pwd, user.get("password")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Couldn't validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    # Check user privileges
    for scope in user.get("scopes"):
        if scope not in settings.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user credentials."
            )
    if exclude:
      for key in exclude:
        user.pop(key) 
    return user

async def get_grades(
        db: AsyncDatabase, 
        *,
        edbo_id: int,
        group: str,
        **kwargs
    ) -> dict:
    """
    Get student subject grades.
    """
    collection = db.get_collection(group)
    grades_doc: dict = await collection.find_one({"edbo_id": edbo_id})
    if not grades_doc: return {}
    disciplines: dict = grades_doc.get("disciplines", {})
    subject, date = kwargs.get("subject"), kwargs.get("date")
    if subject and date: return disciplines.get(subject, {}).get(date)
    if subject: return disciplines.get(subject, {})
    result = {}
    for subject, records in disciplines.items():
        result[subject] = records.get(date) if date else records
    return result