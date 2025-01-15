from fastapi import APIRouter
from core.schemas.user import (
    UserCreate,
    UserDelete
)

import crud

router = APIRouter(tags=["Users"])

@router.post("/create-user")
async def create_user(user: UserCreate):
    return await crud.create_user(user_create=user)

@router.delete("/delete-user", response_model=bool)
async def delete_user(user: UserDelete) -> bool:
    return await crud.delete_user(edbo_id=user.edbo_id)