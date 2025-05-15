from fastapi import Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,
    SecurityScopes
)
from typing import AsyncGenerator
from redis.asyncio import Redis
import json

from core.config import settings

from core.db import RedisClient
from core.security.jwt import OAuthJWTBearer
from core.schemas.etc import TokenData
from core.schemas.user import UserDB
import crud

async def get_redis() -> AsyncGenerator:
    if not RedisClient.client:
        await RedisClient.connect()
    yield RedisClient.client 

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    scopes=settings.scopes)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis)
) -> dict:
    payload = OAuthJWTBearer.decode(token=token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Couldn't validate user credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    username = payload.get("sub")
    user = json.loads(await redis.get(f"oauth:token:{token}"))
    if not user:
        UserDB.COLLECTION_NAME = payload.get("role")
        user = await crud.get_user_by_username(username=username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Couldn't validate user credentials.",
                headers={"WWW-Authenticate": "Bearer"}
            )
    scopes = user.get("scopes")
    token_data = TokenData(edbo_id=user.get("edbo_id"), scopes=scopes)
    if security_scopes.scopes:
        for scope in token_data.scopes:
            if scope not in security_scopes.scopes:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Not enough permissions")
    return user