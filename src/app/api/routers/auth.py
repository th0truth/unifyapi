from typing import Annotated
from datetime import timedelta
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

from core.config import settings
from core.schemas.token import TokenBase, TokenPayload
from core.security.jwt import OAuthJWTBearer
from api.dependencies import (
  get_mongo_client,
  get_redis_client,
  get_current_user
)
import crud

router = APIRouter(tags=["Authentication"])

@router.post("/login",
  status_code=status.HTTP_200_OK,
  response_model=TokenPayload)
async def login(
  form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)],
  redis: Annotated[Redis, Depends(get_redis_client)] 
):
  """
  Log in using user credentials.
  """
  # Authenticate user credentials from the MongoDB database
  users_db = mongo.get_database("users")
  user = await crud.authenticate_user(users_db, username=form_data.username, plain_pwd=form_data.password, exclude=["_id", "password"])
  
  # Get data from the payload   
  edbo_id, role, scope = user.get("edbo_id"), user.get("role"), user.get("scope") 

  # Encode user payload for get an JWT
  token = OAuthJWTBearer.encode(payload={"sub": str(edbo_id), "role": role, "scope": scope})
  
  # Store user credentials in Redis database
  await redis.setex(f"auth:user:{edbo_id}", timedelta(minutes=settings.CACHE_EXPIRE_MINUTES).seconds, json.dumps(user, default=str))

  return TokenPayload(access_token=token["jwt"], role=role)

@router.post("/token",
  status_code=status.HTTP_200_OK,
  response_model=TokenPayload)
async def auth_token(
  token: Annotated[TokenBase, Header(alias="Authorization")],
  redis: Annotated[Redis, Depends(get_redis_client)]
):
  """
  Log in using an access token.
  """
  # Decode a user's JWT
  payload = OAuthJWTBearer.decode(token.access_token)
  if not payload:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Invalid token."
    )
  
  # Get variables from the payload   
  role, jti, exp = payload.get("role"), payload.get("jti"), payload.get("exp") 

  # Check if jti is revoked
  if await OAuthJWTBearer.is_jti_in_blacklist(redis, jti=jti):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Token has been revoked."
    )
    
  # Add the access token to the blacklist
  if not await OAuthJWTBearer.add_jti_to_blacklist(redis, jti=jti, exp=exp):
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Failed to add the token to the blacklist."
    )
  
  # Refresh token
  refresh_token = await OAuthJWTBearer.refresh(payload)

  return TokenPayload(access_token=refresh_token, role=role)

@router.post("/logout",
  status_code=status.HTTP_200_OK,
  dependencies=[Depends(get_current_user)])
async def logout(
  token: Annotated[TokenBase, Header()],
  redis: Annotated[Redis, Depends(get_redis_client)]
):
  """
  Log out from user account.
  """
  # Decode a user's JWT 
  payload = OAuthJWTBearer.decode(token.access_token)

  # Check if jti is revoked
  if await OAuthJWTBearer.is_jti_in_blacklist(redis, jti=payload.get("jti")):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Token has been revoked."
    )

  # Add the access token to the blacklist
  if not await OAuthJWTBearer.add_jti_to_blacklist(redis, jti=token.access_token, exp=payload.get("exp")):
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail="An error occured while adding JWT to blacklist."
    )
  
  raise HTTPException(
    status_code=status.HTTP_200_OK,
    detail="Successfully logged out."
  )