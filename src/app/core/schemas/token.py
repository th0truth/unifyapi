from pydantic import BaseModel
from typing import List

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: int | str
    scopes: List[str] = []