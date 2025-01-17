from fastapi.security import (
    OAuth2PasswordBearer,
    SecurityScopes
)
from fastapi import Depends
from typing import Annotated

from core.config import settings
from core.security.jwt import decode_token
from core.schemas.user import UserDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_token(token=token)
    edbo_id: int | None = int(payload.get("sub"))
    return await UserDB.find_by({"edbo_id": edbo_id})