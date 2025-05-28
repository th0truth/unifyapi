from fastapi.security import OAuth2PasswordRequestForm
from fastapi import (
    HTTPException,
    APIRouter,
    status,
    Depends,
    Header,
)
from redis.asyncio import Redis
import json

from core.db import MongoClient

from core.logger import logger
from core.config import settings
from core.schemas.etc import Token
from core.security.jwt import OAuthJWTBearer
from api.dependencies import (
    get_mongo_client,
    get_redis_client,
    get_current_user
)
import crud

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login_via_credentials(
        form_data: OAuth2PasswordRequestForm = Depends(),
        mongo: MongoClient = Depends(get_mongo_client),
        redis: Redis = Depends(get_redis_client) 
    ):
    """
    Log in using user credentials.
    """
    access_token = await redis.get(f"oauth:user:{form_data.username}")
    if access_token:
        return Token(access_token=access_token) 
    user_db = mongo.get_database("users")
    user = await crud.authenticate_user(user_db, username=form_data.username, plain_pwd=form_data.password, exclude=["_id", "password"])
    access_token = OAuthJWTBearer.encode(
        payload={"sub": str(user.get("edbo_id")), "role": user.get("role"), "scope": form_data.scopes or user.get("scopes")})
    try:
        await redis.setex(f"oauth:token:{access_token}", settings.JWT_EXPIRE_MIN * 60, json.dumps(user, default=str))
        await redis.setex(f"oauth:user:{form_data.username}", settings.JWT_EXPIRE_MIN * 60, access_token)
    except Exception as err:
        logger.error({"msg": "Failed adding `token` and `user` to Redis.", "detail": err})
    return Token(access_token=access_token)

@router.post("/token", response_model=Token)
async def auth_token(
        token: Token = Header(alias="Authorization"),
        redis: Redis = Depends(get_redis_client)
    ):
    """
    Log in using an access token.
    """
    if await OAuthJWTBearer.is_jwt_in_blacklist(token.access_token, redis):
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
    
    user = await redis.get(f"oauth:token:{token.access_token}")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token."
        )
        
    if not await OAuthJWTBearer.add_jwt_to_blacklist(token.access_token, payload.get("exp"), redis):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed deal with token."
        )
    refresh_token = await OAuthJWTBearer.refresh(payload)
    username = payload.get("sub") 
    try:
        await redis.delete(f"oauth:token:{token.access_token}")
        await redis.delete(f"oauth:user:{username}")
    finally:
        await redis.setex(f"oauth:token:{refresh_token}", settings.JWT_EXPIRE_MIN * 60, user)
        await redis.setex(f"oauth:user:{username}", settings.JWT_EXPIRE_MIN * 60, refresh_token)
    return Token(access_token=refresh_token)

@router.post("/logout", dependencies=[Depends(get_current_user)])
async def logout(token: Token = Header()):
    """
    Log out from user account.
    """
    if not await OAuthJWTBearer.add_jwt_to_blacklist(jti=token.access_token):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An error occured while adding JWT to blacklist."
        )
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="Successfully logged out."
    )