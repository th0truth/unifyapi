from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Header, Depends
from typing import Annotated

from core.security.jwt import OAuthJWTBearer
from core.schemas.token import Token
import crud

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login_access_token(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
        Login with user credentials.
    """
    user = await crud.authenticate_user(edbo_id=int(form.username), plain_pwd=form.password)
    token = OAuthJWTBearer.encode(payload={"sub": str(user["edbo_id"]), "scopes": form.scopes})
    return Token(access_token=token)

@router.post("/token", response_model=Token)
async def auth_token(token: Annotated[str, Header()]):
    """
        Login with an access token.
    """
    return await OAuthJWTBearer.verify(token=token)

