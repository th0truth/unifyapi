from typing import Annotated
from fastapi import (
    APIRouter,
    Security,
    Depends,
    Body,
    Path
)

from core.schemas.user import (
    UserUpdate,
    UserDelete,
    UserPublic,
    UserPrivate,
    UserDB
)
import api.deps as deps
import crud

router = APIRouter(tags=["Users"])

UserDB.DATABASE_NAME = "users"

@router.get("/read/{edbo_id}", response_model=UserPublic, 
            dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def read_user_by_edbo_id(edbo_id: int = Path()):
    """
        Return user data by 'edbo_id'.  
    """
    return await crud.read_user(edbo_id=edbo_id)

@router.patch("/update/profile/{edbo_id}", dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def update_user(edbo_id: int, user_update: UserUpdate):
    """
        Update user data by 'edbo_id'.
    """
    return await crud.update_user(edbo_id=edbo_id, update=user_update)

@router.patch("/update/me")
async def update_current_user(
    user: Annotated[UserPrivate, Depends(deps.get_current_user)], user_update: UserUpdate):
    """
        Update current user data. 
    """
    return await crud.update_user(edbo_id=user.get("edbo_id"), update=user_update)

@router.get("/me", response_model=UserPrivate)
async def get_current_user(user: Annotated[UserPrivate, Depends(deps.get_current_user)]):
    """
        Return the user's private data.
    """
    return user

@router.delete("/delete", dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def delete_user(user: UserDelete = Body()):
    """
        Delete an exiting user account.
    """
    return await crud.delete_user(user)