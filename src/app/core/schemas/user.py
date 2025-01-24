from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Literal

from core.db.database import MongoDB

ROLE = Literal["students", "teachers", "admins"]

class User(BaseModel):
    edbo_id: int
    name: str
    age: int
    dob: str
    role: ROLE = "students"
    scopes: list

class UserCreate(User):
    datetime: datetime
    password: str = Field(..., min_length=8, max_length=16)

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None

class UserDelete(BaseModel):
    edbo_id: int
    email: EmailStr | None = None

class UserPrivate(BaseModel):
    edbo_id: int
    phone_number: str
    email: EmailStr | None = None
    password: str

class UserDB(MongoDB):
    DATABASE_NAME: str
    COLLECTION_NAME: str