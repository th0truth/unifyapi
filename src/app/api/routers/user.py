from fastapi import (
    HTTPException,
    APIRouter,
    status,
    Depends,
    Body,
)
from core.security.utils import Hash
from core.schemas.user import (
    UserPrivate,
    UserUpdate,
    UserDB,
    ROLE
)
from core.schemas.teacher import Teacher
from core.schemas.group import GroupDB
from core.schemas.etc import (
    UpdatePassword,
    PasswordRecovery
)

import api.dependencies as deps 
import crud

router = APIRouter(tags=["User"])

@router.get("/me", response_model=UserPrivate)
async def get_current_user(user: dict = Depends(deps.get_current_user)):
    """
    Read the user's private data.
    """
    return user

@router.patch("/update/email")
async def add_user_email(
        user: dict = Depends(deps.get_current_user),
        user_update: UserUpdate = Body()
    ):
    """
    Add email to the user account.
    """
    if await crud.get_user_by_username(username=user_update.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That email is already associated with another account.")
    user = await crud.authenticate_user(username=user.get("edbo_id"), plain_pwd=user_update.password) 
    await crud.update_user(
        edbo_id=user.get("edbo_id"),
        data={"email": user_update.email}
    )

@router.patch("/update/password")
async def update_password_me(
        user: dict = Depends(deps.get_current_user),
        body: UpdatePassword = Body()
    ):
    """
    Update own passoword.
    """
    user = await crud.authenticate_user(username=user.get("edbo_id"), plain_pwd=body.current_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    await crud.update_user(
        edbo_id=user.get("edbo_id"), data={"password": Hash.hash(plain=body.new_password)})

@router.patch("/password-recovery")
async def password_recovery(body: PasswordRecovery = Body()):
    """
    Password recovery.
    """
    user = await crud.get_user_by_username(username=body.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    await crud.update_user(edbo_id=user.get("edbo_id"), data={"password": Hash.hash(plain=body.new_password)})

@router.get("/disciplines")
async def get_user_disciplines(user: dict = Depends(deps.get_current_user)):
    """
    Read the user's disciplines.
    """
    role: ROLE = user.get("role")
    match role:
        case "students":
            disciplines = {}
            GroupDB.COLLECTION_NAME = user.get("degree")
            group = await GroupDB.find_by({"group": user.get("group")})
            if not group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Your group not found in the system."
                )
            for discipline, edbo_id in group.get("disciplines").items():
                UserDB.COLLECTION_NAME = "teachers"
                disciplines.update(
                    {discipline: Teacher(**await UserDB.find_by({"edbo_id": edbo_id}))})
        case "teachers":
            disciplines = user.get("disciplines")
    return disciplines