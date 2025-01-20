from authlib.integrations.starlette_client import OAuth

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Request, Header, Depends
from typing import Annotated

from core.config import settings

from core.security.jwt import OAuthJWTBearer
from core.schemas.user import UserDB
from core.schemas.token import Token
import crud

router = APIRouter(tags=["Authentication"])

UserDB.DATABASE_NAME = "college"
UserDB.COLLECTION_NAME = "ipz12"

oauth = OAuth()

oauth.register(
    name=settings.NAME,
    client=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    refresh_token_url=None,
    authorize_state=settings.SECRET_KEY,
    redirect_url="http://localhost:8000/api/v1/auth/google",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    client_kwargs={"scope": "openid profile email"},
)

@router.post("/login/credentials", response_model=Token)
async def login_via_credentials(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
        Login with user credentials.
    """
    user = await crud.authenticate_user(edbo_id=int(form.username), plain_pwd=form.password)
    token = OAuthJWTBearer.encode(payload={"sub": str(user["edbo_id"]), "scopes": form.scopes})
    return Token(access_token=token)

@router.post("/login/google")
async def login_via_google(request: Request):
    request.session.clear()

@router.post("/google")
async def auth_via_google(request: Request):
    google = oauth.create_client("google")
    token = await google.authorize_access_token(request)
    print(token)
    # url = request.url_for("auth")
    # try:
        # token = await oauth.

@router.post("/token", response_model=Token)
async def auth_token(token: Annotated[str, Header()]):
    """
        Login with an access token.
    """
    return await OAuthJWTBearer.verify(token=token)

