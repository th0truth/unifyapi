from fastapi import Depends
from fastapi.security import (
    OAuth2PasswordBearer,
    SecurityScopes
)

from core.config import settings
from core.security.jwt import OAuthJWTBearer
from core.schemas.etc import TokenData
from core.schemas.user import UserDB
from core import exc

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/credentials",
    scopes=settings.scopes)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
) -> dict:
    payload = OAuthJWTBearer.decode(token=token)
    if not payload:
        raise exc.UNAUTHORIZED(deta="Invalid user credentials.")
    UserDB.COLLECTION_NAME = payload.get("role")
    edbo_id = int(payload.get("sub"))
    scopes = payload.get("scopes")
    if not scopes:
        user = await UserDB.find_by({"edbo_id": edbo_id})
        if not user:
            raise exc.NOT_FOUND(
                detail="Something went wrong. Try again later.")
        scopes = user.get("scopes")
    token_data = TokenData(edbo_id=edbo_id, scopes=scopes)
    if security_scopes.scopes:
        for scope in token_data.scopes:
            if scope not in security_scopes.scopes:
                raise exc.UNAUTHORIZED(
                    detail="Not enough permissions")
    user = await UserDB.find_by({"edbo_id": edbo_id})
    if not user:
        raise exc.INTERNAL_SERVER_ERROR(
            detail="Something went wrong. Try again later.")
    return user