from typing import Annotated, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,
    SecurityScopes
)
from redis.asyncio import Redis
import json

from core.config import settings

from core.security.jwt import OAuthJWTBearer
from core.db import MongoClient, RedisClient
from core.schemas.etc import TokenData
import crud

async def get_mongo_client() -> AsyncGenerator[MongoClient, None]:
    """Dependency to get MongoDB client."""
    if not MongoClient._client:
        await MongoClient.connect()
    yield MongoClient._client

async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """Dependency to get Redis client."""
    if not RedisClient._client:
        await RedisClient.connect()
    yield RedisClient._client

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    scopes=settings.scopes)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    mongo: Annotated[MongoClient, Depends(get_mongo_client)],
    redis: Annotated[Redis, Depends(get_redis_client)]
) -> dict:
    payload: dict = OAuthJWTBearer.decode(token=token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Couldn't validate user credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    username = payload.get("sub")
    user: dict = json.loads(await redis.get(f"session:token:{token}"))
    if not user:
        user_db = mongo.get_database("users")
        user_db.get_collection(name=payload["role"])
        user = await crud.get_user_by_username(username=username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Couldn't validate user credentials.",
                headers={"WWW-Authenticate": "Bearer"}
            )
    token_data = TokenData(edbo_id=user["edbo_id"], scopes=user["scopes"])
    if security_scopes.scopes:
        for scope in token_data.scopes:
            if scope not in security_scopes.scopes:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Not enough permissions"
                )
    return user