from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Literal, List

from core.db.database import MongoDB

ROLE = Literal["students", "teachers", "admins"]

class User(BaseModel):
    edbo_id: int
    first_name: str
    middle_name: str
    last_name: str 
    date_of_birth: str
    phone_number: List[int]
    role: ROLE
    scopes: list
    password: str

class UserCreate(User):
    acc_date: datetime
    password: str = Field(..., min_length=8, max_length=16)

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str

class UserDelete(BaseModel):
    username: str

class UserPublic(BaseModel):
    edbo_id: int
    first_name: str
    middle_name: str
    last_name: str
    role: str

class UserDB(MongoDB):
    DATABASE_NAME: str
    COLLECTION_NAME: str