from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    Body,
)

from core.security.utils import Hash
from core.schemas.user import (
    UserUpdate,
    UserPrivate,
)
from core.schemas.utils import (
    UpdatePassword,
    PasswordRecovery
)
from core import exc
import api.deps as deps
import crud

router = APIRouter(tags=["User"])

@router.get("/me", response_model=UserPrivate)
async def get_current_user(user_private: Annotated[UserPrivate, Depends(deps.get_current_user)]):
    """
        Return the user's private data.
    """
   
    return user_private

@router.patch("/update")
async def update_current_user(
    user: Annotated[UserPrivate, Depends(deps.get_current_user)], user_update: UserUpdate = Body()):
    """
        Update current user data. 
    """
    
    await crud.update_user(edbo_id=user.get("edbo_id"), data=user_update.model_dump())  

@router.patch("/update/password")
async def update_password_me(user_private: Annotated[UserPrivate, Depends(deps.get_current_user)],
                             body: Annotated[UpdatePassword, Body()]):
    """
        Update own passoword.
    """
    user = await crud.authenticate_user(username=user_private.get("edbo_id"), plain_pwd=body.current_password)
    if not user:
        raise exc.UNAUTHORIZED(detail="Incorrect password")
    await crud.update_user(
        edbo_id=user.get("edbo_id"), data={"password": Hash.hash(plain=body.new_password)})

@router.patch("/password-recovery")
async def password_recovery(body: Annotated[PasswordRecovery, Body()]):
    """
        Password recovery.
    """

    user = await crud.get_user_by_username(username=body.email)
    if not user:
        raise exc.NOT_FOUND(detail="User not found.")
    await crud.update_user(edbo_id=user.get("edbo_id"), data={"password": Hash.hash(body.new_password)})