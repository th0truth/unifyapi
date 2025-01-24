from authlib.integrations.starlette_client import OAuth
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Request, Header, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
from pathlib import Path

from core.config import settings
from core.security.jwt import OAuthJWTBearer
from core.schemas.user import UserDB
from core.schemas.token import Token
from core import exc
import requests
import crud

router = APIRouter(tags=["Authentication"])

UserDB.DATABASE_NAME = "users"

# Setup Google OAuth2 
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

# Load Jinja2 templates
BASE_PATH = Path(__file__).parent.parent.parent
templates = Jinja2Templates(directory=BASE_PATH / "templates") 

@router.post("/login/credentials", response_model=Token)
async def login_via_credentials(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
        Login with user credentials.
    """
    user = await crud.authenticate_user(username=form_data.username, plain_pwd=form_data.password)
    token = OAuthJWTBearer.encode(
        payload={"sub": str(user["edbo_id"]), "scope": form_data.scopes})
    return Token(access_token=token)

@router.post("/token", response_model=Token)
async def auth_token(token: str = Header()):
    """
        Login with an access token.
    """
    return await OAuthJWTBearer.verify(token=token)

@router.get("/login/google", deprecated=True)
async def login_via_google(request: Request):
    """
        Redirect to Google OAuth2.
    """
    return await oauth.google.authorize_redirect(request, settings.REDIRECT_URL, prompt="consent")

@router.route("/google")
async def auth_google(request: Request):
    """
        Authorization via google
    """
    try:
        token: dict = await oauth.google.authorize_access_token(request)
    except:
        return templates.TemplateResponse(
            request=request, name="/google_auth/failed.html")
    try:
        headers = {"Authorization": f"Bearer {token['access_token']}"}
        response: dict = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers).json()
    except:
        return templates.TemplateResponse(
            request=request, name="/google_auth/failed.html")

    user_info = token.get("userinfo")
    if not user_info: 
        return templates.TemplateResponse(
            request=request, name="/google_auth/failed.html")

    # Search user by email
    email = response.get("email")  
    user = await crud.get_user_by_username(username=email)
    if not user:
        return templates.TemplateResponse(
            request=request, name="/email/failed.html")
    access_token = OAuthJWTBearer.encode(
        payload={"sub": user.get("sub"), "scope": user.get("scopes")})
    

    # response = templates.TemplateResponse(
        # request={"request": request}, name="/google_auth/successful.html")
    # response.headers["X-Access-Token"] = access_token 
    return 