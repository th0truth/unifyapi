from fastapi import APIRouter, Security
from core.schemas.user import (
    UserCreate,
    UserDelete
)

from typing import Annotated

import api.deps as deps
import crud

router = APIRouter(tags=["Users"])

@router.post("/create-user")
async def create_user(user: Annotated[UserCreate, Security(deps.get_current_user, scopes=["admin"])]):
    """
        Create a new user account.
    """
    return await crud.create_user(user=user)

@router.delete("/delete-user")
async def delete_user(user: Annotated[UserDelete, Security(deps.get_current_user, scopes=["admin"])]):
    """
        Delete an exiting user account.
    """
    return await crud.delete_user(user)