from pydantic import BaseModel, Field
from typing import Annotated

PASSWORDstr = Annotated[str, Field(..., min_length=8, max_length=128)]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(Token):
    role: str

class TokenData(BaseModel):
    edbo_id: int
    scopes: list

class UpdatePassword(BaseModel):
    current_password:  PASSWORDstr
    new_password: PASSWORDstr

class PasswordRecovery(BaseModel):
    email: str
    new_password: PASSWORDstr