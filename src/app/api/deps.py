from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from typing import Annotated

from core.config import settings
from core.security.jwt import decode_token
from core.schemas.user import UserDB

oauth2_scheme = OAuth2PasswordBearer(f"{settings.API_V1_STR}/login/access-token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_token(token)
    edbo_id: int | None = int(payload.get("sub"))
    return await UserDB.find_by({"edbo_id": edbo_id})