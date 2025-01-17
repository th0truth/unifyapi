from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Header, Depends
from typing import Annotated

from core.security.jwt import encode_token, decode_token
from core.schemas.user import UserDB
from core.schemas.token import Token
from core import exceptions
import crud

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login_access_token(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await crud.authenticate_user(edbo_id=int(form.username), plain_pwd=form.password)
    access_token = encode_token(payload={"sub": str(user["edbo_id"])})
    return Token(access_token=access_token, token_type="bearer")

@router.post("/token")
async def auth_token(token: Annotated[str, Header()]):
    edbo_id = decode_token(token=token).get("sub")
    user = await UserDB.find_by({"edbo_id": int(edbo_id)})
    if not user:
        raise exceptions.UNAUTHORIZED(
            detail="Couldn't validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    raise exceptions.OK(
        detail="Successful Authentication")
