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
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    scopes=settings.scopes)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
) -> dict:
    payload = OAuthJWTBearer.decode(token=token)
    if not payload:
        raise exc.UNAUTHORIZED(
            detail="Invalid user credentials."
        )
    UserDB.COLLECTION_NAME = payload.get("role")
    edbo_id = int(payload.get("sub"))
    user = await UserDB.find_by({"edbo_id": edbo_id})
    scopes = user.get("scopes")
    token_data = TokenData(edbo_id=edbo_id, scopes=scopes)
    if security_scopes.scopes:
        for scope in token_data.scopes:
            if scope not in security_scopes.scopes:
                raise exc.UNAUTHORIZED(
                    detail="Not enough permissions")
    return user