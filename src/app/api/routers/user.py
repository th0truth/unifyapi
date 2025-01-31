from fastapi import (
    APIRouter,
    Depends,
    Body,
)

from core.security.utils import Hash
from core.schemas.user import (
    User,
    UserUpdate,
)
from core.schemas.utils import (
    UpdatePassword,
    PasswordRecovery
)
from core import exc
import api.deps as deps
import crud

router = APIRouter(tags=["User"])

@router.get("/me", response_model=User)
async def get_current_user(user: User = Depends(deps.get_current_user)):
    """
        Return the user's private data.
    """
   
    return user

@router.patch("/add-email")
async def add_user_email(
    user: dict = Depends(deps.get_current_user), user_update: UserUpdate = Body()):
    """
        Add email to the user account.
    """

    if await crud.get_user_by_username(username=user_update.email):
        raise exc.CONFLICT(
            detail="That email is already associated with another account.")
    user = await crud.authenticate_user(username=user.get("edbo_id"), plain_pwd=user_update.password) 
    await crud.update_user(
        edbo_id=user.get("edbo_id"),
        data={"email": user_update.email}
    )

@router.patch("/update/password")
async def update_password_me(user: dict = Depends(deps.get_current_user),
                             body: UpdatePassword = Body()):
    """
        Update own passoword.
    """

    user = await crud.authenticate_user(username=user.get("edbo_id"), plain_pwd=body.current_password)
    if not user:
        raise exc.UNAUTHORIZED(detail="Incorrect password")
    await crud.update_user(
        edbo_id=user.get("edbo_id"), data={"password": Hash.hash(plain=body.new_password)})

@router.patch("/password-recovery")
async def password_recovery(body: PasswordRecovery = Body()):
    """
        Password recovery.
    """

    user = await crud.get_user_by_username(username=body.email)
    if not user:
        raise exc.NOT_FOUND(detail="User not found.")
    await crud.update_user(edbo_id=user.get("edbo_id"), data={"password": Hash.hash(body.new_password)})