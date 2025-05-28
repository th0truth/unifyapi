from typing import Annotated, Optional, List
from fastapi import (
    APIRouter,
    Security,
    Depends,
    Body,
    Path,
)

from core.db import MongoClient

from core.schemas.user import UserBase, UserUpdate
from api.dependencies import (
    get_mongo_client,
    get_current_user
)
import crud

router = APIRouter(tags=["Users"])
    
@router.get("/read/{edbo_id}", response_model=UserBase,
    dependencies=[Security(get_current_user, scopes=["teacher", "admin"])])
async def read_user(
        edbo_id: Annotated[int, Path],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Return user data by `edbo_id`.
    """
    user_db = mongo.get_database("users")
    return await crud.read_user(user_db, edbo_id=edbo_id)

@router.get("/read/{role}/all", response_model=List[UserBase],
    dependencies=[Security(get_current_user, scopes=["admin"])])
async def read_users(
        role: Annotated[str, Path],
        filter: Annotated[None, Optional[str]],
        value: Annotated[None, Optional[str]],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]   
    ):
    """
    Return all users.
    """
    user_db = mongo.get_database("users")
    return await crud.read_users(user_db, role=role, filter=filter, value=value)

@router.patch("/update/{edbo_id}",
    dependencies=[Security(get_current_user, scopes=["teacher", "admin"])])
async def update_user(
        edbo_id: Annotated[int, Path],
        update_doc: Annotated[UserUpdate, Body],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Update user data by `edbo_id`.
    """
    user_db = mongo.get_database("users")
    await crud.update_user(user_db, edbo_id=edbo_id, update_doc=update_doc)

@router.patch("/update/all",
    dependencies=[Security(get_current_user, scopes=["admin"])])
async def update_all_users(
        role: Annotated[str, Path],
        update_doc: Annotated[UserUpdate, Body],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Update users data.
    """
    user_db = mongo.get_database("users")
    await crud.update_all_users(user_db, role=role, update_doc=update_doc)

@router.delete("/delete/{edbo_id}",
    dependencies=[Security(get_current_user, scopes=["admin"])])
async def delete_user(
        edbo_id: Annotated[int, Path],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)] 
    ):
    """
    Delete an exiting user account.
    """
    user_db = mongo.get_database("users")
    return await crud.delete_user(user_db, edbo_id=edbo_id)