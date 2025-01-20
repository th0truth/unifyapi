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

from core import exceptions

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    scopes=settings.scopes)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)]
) -> dict:
    payload = OAuthJWTBearer.decode(token=token)
    edbo_id: int | None = int(payload.get("sub"))
    token_data = TokenData(scopes=payload.get("scopes"), username=edbo_id)
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise exceptions.UNAUTHORIZED(
                detail="Not enough permissions")
    return await UserDB.find_by({"edbo_id": edbo_id})