from fastapi.security import OAuth2PasswordRequestForm
from fastapi import (
    HTTPException,
    APIRouter,
    status,
    Depends,
    Header,
)

from api.deps import get_current_user

from core.security.jwt import OAuthJWTBearer
from core.schemas.etc import Token
import crud

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login_via_credentials(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Log in using user credentials.
    """
    user = await crud.authenticate_user(username=form_data.username, plain_pwd=form_data.password)
    token = OAuthJWTBearer.encode(
        payload={"sub": str(user.get("edbo_id")), "role": user.get("role"), "scope": form_data.scopes or user.get("scopes")})
    return Token(access_token=token)

@router.post("/token", response_model=Token)
async def auth_token(token: Token = Header()):
    """
    Log in using an access token.
    """
    response = await OAuthJWTBearer.is_jti_in_blacklist(jti=token.access_token)
    if response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked."
        )
    payload = OAuthJWTBearer.decode(token=token.access_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Couldn't validate user credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    response = await OAuthJWTBearer.add_jti_to_blacklist(jti=token.access_token)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An error occured while adding token to blacklist."
        )
    refresh_token = OAuthJWTBearer.refresh(payload=payload)
    return Token(access_token=refresh_token)

@router.post("/logout", dependencies=[Depends(get_current_user)])
async def logout(token: Token = Header()):
    """
    Log out from user account.
    """
    response = await OAuthJWTBearer.add_jti_to_blacklist(jti=token.access_token)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An error occured while adding JWT to blacklist."
        )
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="Successfully logged out."
    )