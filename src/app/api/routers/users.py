from fastapi import APIRouter, Body, Security, Depends
from core.schemas.user import (
    UserCreate,
    UserDelete,
    UserPrivate
)

from typing import Annotated
import api.deps as deps
import crud

from core.schemas.user import UserDB

router = APIRouter(tags=["Users"])

UserDB.COLLECTION_NAME = "ipz12"

@router.post("/create") #dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def create_user(user: UserCreate = Body()):
    """
        Create a new user account.
    """
    return await crud.create_user(user=user)

@router.delete("/delete", dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def delete_user(user: Annotated[UserDelete, Body()]):
    """
        Delete an exiting user account.
    """
    return await crud.delete_user(user)

@router.get("/me", response_model=UserPrivate)
async def get_current_user(user: Annotated[UserPrivate, Depends(deps.get_current_user)]):
    """
        Return the user's private data.
    """
    return user