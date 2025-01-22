from authlib.integrations.starlette_client import OAuth
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Request, Header, Depends
from typing import Annotated

from core.config import settings
from core.security.jwt import OAuthJWTBearer
from core.schemas.user import UserDB
from core.schemas.token import Token
from core import exc
import requests
import crud

router = APIRouter(tags=["Authentication"])

UserDB.DATABASE_NAME = "users"

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    refresh_token_url=None,
    authorize_state=settings.SECRET_KEY,
    redirect_uri=settings.REDIRECT_URL,
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    client_kwargs={"scope": "openid profile email"},
)

@router.post("/login/credentials", response_model=Token)
async def login_via_credentials(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
        Login with user credentials.
    """
    user = await crud.authenticate_user(username=form_data.username, plain_pwd=form_data.password)
    token = OAuthJWTBearer.encode(
        payload={"edbo_id": user["edbo_id"], "scopes": form_data.scopes})
    return Token(access_token=token)

@router.get("/login/google")
async def login_via_google(request: Request):
    return await oauth.google.authorize_redirect(request, settings.REDIRECT_URL, prompt="consent")

@router.post("/token", response_model=Token)
async def auth_token(token: Annotated[str, Header()]):
    """
        Login with an access token.
    """
    return await OAuthJWTBearer.verify(token=token)

@router.get("/google")
async def auth_via_google(request: Request):
    """
        Authorization via google
    """
    try:
        token: dict = await oauth.google.authorize_access_token(request)
    except:
        raise exc.UNAUTHORIZED(
            detail="Google authentication failed.")
    try:
        headers = {"Authorization": f"Bearer {token["access_token"]}"}
        response: dict = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers).json()
    except:
        raise exc.UNAUTHORIZED(
            detail="Google authentication failed.")

    user_info: dict = token.get("userinfo")
    user_id = user_info.get("sub")
    iss = user_info.get("iss")    

    if user_id is None or iss not in ["https://accounts.google.com","accounts.google.com"]: 
        raise exc.UNAUTHORIZED(detail="Google authentication failed.")

    email = response.get("email")  
    user = await crud.get_user_by_username(username=email)
    if not user:
        raise exc.UNAUTHORIZED(detail="Google authentication failed.") 
    access_token = OAuthJWTBearer.encode(
        payload={"edbo_id": user.get("edbo_id"), "scopes": user.get("scopes")})
    return Token(access_token=access_token)