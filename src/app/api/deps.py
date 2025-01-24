from fastapi.security import (
    OAuth2PasswordBearer,
    SecurityScopes
)
from fastapi import Depends
from typing import Annotated

from core.config import settings
from core.security.jwt import OAuthJWTBearer
from core.schemas.token import TokenData
from core.schemas.user import UserDB

from core import exc

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/credentials",
    scopes=settings.scopes)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)]
) -> dict:
    payload = OAuthJWTBearer.decode(token=token)
    if not payload:
        raise exc.UNAUTHORIZED(deta="Invalid user credentials.")
    UserDB.COLLECTION_NAME = payload.get("role")
    edbo_id = int(payload.get("sub"))
    token_data = TokenData(edbo_id=edbo_id, scopes=payload.get("scope"))
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise exc.UNAUTHORIZED(
                detail="Not enough permissions")
    return await UserDB.find_by({"edbo_id": edbo_id})