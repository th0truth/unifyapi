from fastapi.security import OAuth2PasswordRequestForm
from fastapi import (
    APIRouter,
    Depends,
    Header
)
from typing import Annotated

from core.security.jwt import OAuthJWTBearer
from core.schemas.etc import Token
import crud

router = APIRouter(tags=["Authentication"])

@router.post("/login/credentials", response_model=Token)
async def login_via_credentials(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
        Login with user credentials.
    """
    user = await crud.authenticate_user(username=form_data.username, plain_pwd=form_data.password)
    token = OAuthJWTBearer.encode(
        payload={"sub": str(user.get("edbo_id")), "role": user.get("role"), "scope": form_data.scopes or user.get("scopes")})
    return Token(access_token=token)

@router.post("/token", response_model=Token)
async def auth_token(token: str = Header()):
    """
        Login with an access token.
    """
    return await OAuthJWTBearer.verify(token=token)

@router.post("/logout")
async def logout(token: Token = Header()):
    pass