from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import (
    HTTPException,
    APIRouter,
    status,
    Depends,
    Header,
)
import json

from redis.asyncio import Redis
from core.db import MongoClient

from core.logger import logger
from core.config import settings
from core.schemas.etc import Token, TokenPayload
from core.security.jwt import OAuthJWTBearer
from api.dependencies import (
    get_mongo_client,
    get_redis_client,
    get_current_user
)
import crud

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=TokenPayload)
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)],
        redis: Annotated[Redis, Depends(get_redis_client)] 
    ):
    """
    Log in using user credentials.
    """
    access_token = await redis.get(f"session:user:{form_data.username}")
    if access_token:
        payload = OAuthJWTBearer.decode(token=access_token)
        return TokenPayload(access_token=access_token, role=payload.get("role"))
    user_db = mongo.get_database("users")
    user = await crud.authenticate_user(user_db, username=form_data.username, plain_pwd=form_data.password, exclude=["_id", "password"])
    role, scope = user.get("role"), user.get("scopes")
    access_token = OAuthJWTBearer.encode(
        payload={"sub": str(user.get("edbo_id")), "role": role, "scope": scope})
    try:
        await redis.setex(f"session:token:{access_token}", settings.JWT_EXPIRE_MIN * 60, json.dumps(user, default=str))
        await redis.setex(f"session:user:{form_data.username}", settings.JWT_EXPIRE_MIN * 60, access_token)
    except Exception as err:
        logger.error({"msg": "Failed adding `token` and `user` to Redis.", "detail": err})
    return TokenPayload(access_token=access_token, role=role)

@router.post("/token", response_model=TokenPayload)
async def auth_token(
        token: Annotated[Token, Header(alias="Authorization")],
        redis: Annotated[Redis, Depends(get_redis_client)]
    ):
    """
    Log in using an access token.
    """
    if await OAuthJWTBearer.is_jwt_in_blacklist(redis, jti=token.access_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked."
        )
    
    payload = OAuthJWTBearer.decode(token.access_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token."
        )
    
    user = await redis.get(f"session:token:{token.access_token}")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token."
        )
    
    exp = payload.get("exp")
    if not await OAuthJWTBearer.add_jwt_to_blacklist(redis, jti=token.access_token, exp=exp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed deal with token."
        )
    
    refresh_token = await OAuthJWTBearer.refresh(payload)
    username, role = payload.get("sub"), payload.get("role")
    
    try:
        await redis.delete(f"session:token:{token.access_token}")
        await redis.delete(f"session:user:{username}")
    finally:
        await redis.setex(f"session:token:{refresh_token}", settings.JWT_EXPIRE_MIN * 60, user)
        await redis.setex(f"session:user:{username}", settings.JWT_EXPIRE_MIN * 60, refresh_token)

    return TokenPayload(access_token=refresh_token, role=role)

@router.post("/logout", dependencies=[Depends(get_current_user)])
async def logout(
        token: Annotated[Token, Header()],
        redis: Annotated[Redis, Depends(get_redis_client)]
    ):
    """
    Log out from user account.
    """
    exp = OAuthJWTBearer.decode(token.access_token).get("exp")
    if not await OAuthJWTBearer.add_jwt_to_blacklist(redis, jti=token.access_token, exp=exp):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An error occured while adding JWT to blacklist."
        )
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="Successfully logged out."
    )