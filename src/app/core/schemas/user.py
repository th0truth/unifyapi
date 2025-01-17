from pydantic import BaseModel, Field, EmailStr
from typing import Literal

from core.db.database import MongoDB

ROLE = Literal["student", "teacher", "admin"] 

class UserCreate(BaseModel):
    role: ROLE 
    edbo_id: int
    name: str
    email: EmailStr | None = None
    password: str = Field(..., min_length=8, max_length=16)

class UserDelete(BaseModel):
    role: ROLE
    edbo_id: int

class UserDB(MongoDB):
    DATABASE_NAME: str
    COLLECTION_NAME: str