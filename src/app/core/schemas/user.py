from typing import Literal, List
from datetime import datetime
from pydantic import (
    BaseModel,
    EmailStr,
    Field
)

from core.db.database import MongoDB

ROLE = Literal["students", "teachers", "admins"]
DEGREE = Literal["bachelor", "skilled_worker"] 

class User(BaseModel):
    edbo_id: int
    first_name: str
    middle_name: str
    last_name: str 
    date_of_birth: str
    role: ROLE

class UserPrivate(User):
    acc_date: datetime
    email: EmailStr | None = None
    phone_number: List[int] | None = None
    scopes: list

class UserCreate(User):
    acc_date: datetime
    password: str = Field(..., min_length=8, max_length=256)

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str

class UserDB(MongoDB):
    DATABASE_NAME = "users"