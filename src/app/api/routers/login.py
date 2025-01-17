from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Header, Depends
from typing import Annotated

from core.security.jwt import (
    encode_token,
    decode_token,
    refresh_token)
from core.schemas.user import UserDB
from core.schemas.token import Token
from core import exceptions
import crud

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login_access_token(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
        Login with user credentials.
    """
    user = await crud.authenticate_user(edbo_id=int(form.username), plain_pwd=form.password)
    token = encode_token(payload={"sub": str(user["edbo_id"]), "scopes": form.scopes})
    return Token(access_token=token)

@router.post("/token", response_model=Token)
async def auth_token(token: Annotated[str, Header()]):
    """
        Login with an access token.
    """
    payload = decode_token(token=token)
    edbo_id = payload.get("sub")
    user = await UserDB.find_by({"edbo_id": int(edbo_id)})
    if not user:
        raise exceptions.UNAUTHORIZED(
            detail="Couldn't validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = refresh_token(payload=payload)
    return Token(access_token=token)