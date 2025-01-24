from typing import Annotated
from fastapi import (
    APIRouter,
    Body,
    Security,
    Depends
)

from core.schemas.user import (
    UserDelete,
    UserPrivate,
    UserDB
)
import api.deps as deps
import crud

router = APIRouter(tags=["Users"])

UserDB.DATABASE_NAME = "users"

@router.delete("/delete", dependencies=[Security(deps.get_current_user, scopes=["admins"])])
async def delete_user(user: UserDelete = Body()):
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