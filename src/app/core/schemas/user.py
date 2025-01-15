from pydantic import BaseModel, Field, EmailStr
from typing import Literal

from core.db.database import MongoDB

class UserPriviliges(BaseModel):
    pass


class UserCreate(BaseModel):
    role: Literal["student", "teacher", "admin"] 
    edbo_id: int
    name: str
    email: EmailStr | None = None
    password: str = Field(..., min_length=8, max_length=16)

class UserDelete(BaseModel):
    edbo_id: int

class UserDB(MongoDB):
    DATABASE_NAME = "college"
    COLLECTION_NAME = "ipz12"