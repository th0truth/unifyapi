from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends
from typing import Annotated

from core.schemas.utils import Token
from core.security.jwt import encode_token
from core import exceptions
import crud

router = APIRouter(tags=["Login"])

@router.post("/access-token")
async def login_access_token(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await crud.authenticate_user(edbo_id=int(form.username), plain_pwd=form.password)
    if not user:
        raise exceptions.UNAUTHORIZED(
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) 
    access_token = encode_token(payload={"sub": str(user["edbo_id"])})
    return Token(access_token=access_token, token_type="bearer")