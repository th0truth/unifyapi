from pydantic import BaseModel, Field, EmailStr
from typing import List, Literal

from datetime import datetime
from core.db.database import MongoDB

ROLES = ["students", "teachers", "admins"] 
SCOPES = ["students", "teachers", "admins"]

class User(BaseModel):
    edbo_id: int
    phone_number: str | None = None
    first_name: str
    middle_name: str
    last_name: str 
    age: int
    date_of_birth: str
    role: str
    scopes: list

class UserCreate(User):
    datetime: datetime
    password: str = Field(..., min_length=8, max_length=16)

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None

class UserDelete(BaseModel):
    database_name: str
    collection_name: str
    edbo_id: int
    email: EmailStr | None = None

class UserPrivate(BaseModel):
    edbo_id: int
    phone_number: str
    email: EmailStr | None = None
    first_name: str
    middle_name: str
    last_name: str
    password: str

class UserDB(MongoDB):
    DATABASE_NAME: str
    COLLECTION_NAME: str