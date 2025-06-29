from typing import Annotated
from fastapi import (
    HTTPException,
    APIRouter,
    status,
    Depends,
    Body
)

from core.db import MongoClient

from core.security.utils import Hash
from core.schemas.user import UserUpdateEmail
from core.schemas.teacher import TeacherBase
from core.schemas.etc import (
    UpdatePassword,
    PasswordRecovery
)
from api.dependencies import (
    get_mongo_client,
    get_current_user
)
import crud

router = APIRouter(tags=["User"])

@router.get("/me",
    response_model_exclude={"password"},
    response_model_exclude_none=True)
async def get_active_user(
        user: Annotated[dict, Depends(get_current_user)]
    ):
    """
    Read the user's data.
    """
    return user

@router.patch("/update/email")
async def add_user_email(
        user_update: Annotated[UserUpdateEmail, Body()],
        user: Annotated[dict, Depends(get_current_user)],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Add email to the user account.
    """
    user_db = mongo.get_database("users")
    if await crud.get_user_by_username(user_db, username=user_update.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That email is already associated with another account.")
    user = await crud.authenticate_user(user_db, username=user["edbo_id"], plain_pwd=user_update.password)
    await crud.update_user(user_db, edbo_id=user["edbo_id"], update_doc={"email": user_update.email})

@router.patch("/update/password")
async def update_password_me(
        body: Annotated[UpdatePassword, Body()],
        user: Annotated[dict, Depends(get_current_user)],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Update own passoword.
    """
    user_db = mongo.get_database("users")
    user = await crud.authenticate_user(user_db, username=user["edbo_id"], plain_pwd=body.current_password)
    await crud.update_user(user_db, edbo_id=user["edbo_id"], update_doc={"password": Hash.hash(plain=body.new_password)})

@router.patch("/password-recovery")
async def password_recovery(
        body: PasswordRecovery = Body(),
        mongo: MongoClient = Depends(get_mongo_client)
    ):
    """
    Password recovery.
    """
    user_db = mongo.get_database("users")
    user = await crud.get_user_by_username(user_db, username=body.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Couldn't find your account."
        )
    await crud.update_user(user_db, edbo_id=user["edbo_id"], update_doc={"password": Hash.hash(plain=body.new_password)})