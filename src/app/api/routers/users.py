from typing import List, Any
from fastapi import (
    APIRouter,
    Security,
    Body,
    Path,
)

from core.schemas.user import (
    UserDelete,
    UserPublic,
    UserDB,
    ROLE
)
import api.deps as deps
import crud

router = APIRouter(tags=["Users"])

UserDB.DATABASE_NAME = "users"

@router.get("/read/{role}/all", response_model=List[UserPublic],
           dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def read_users(role: str, filter: str | None = None, value: Any = None, skip: int = 0, length: int | None = None):
    """
        Return all users.
    """

    return await crud.read_users(
        role=role, filter=filter, value=value, skip=skip, length=length)

@router.get("/read/{edbo_id}", response_model=UserPublic, 
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_user_by_edbo_id(edbo_id: int = Path()):
    """
        Return user data by 'edbo_id'.
    """

    return await crud.read_user(edbo_id=edbo_id)

@router.patch("/update/{edbo_id}",
              dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def update_user(edbo_id: int, user_update: dict = Body()):
    """
        Update user data by 'edbo_id'. ##### FOR ADMIN
    """

    await crud.update_user(edbo_id=edbo_id, data=user_update)


@router.patch("/update/all",
              dependencies=[Security(deps.get_current_user, scopes=["admin", "teacher"])])
async def update_users(role: ROLE, filter: dict, data: dict):
    """
        Update users data.
    """

    await crud.update_all_users(collection=role, filter=filter, data=data)

@router.delete("/delete",
               dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def delete_user(creds: UserDelete = Body()):
    """
        Delete an exiting user account.
    """

    user = await crud.get_user_by_username(username=creds.username)
    return await crud.delete_user(user=user)