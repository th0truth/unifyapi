from pydantic import BaseModel, Field, EmailStr
from typing import List, Literal

from datetime import datetime
from core.db.database import MongoDB

ROLE = Literal["students", "teachers", "admins"] 
PRIVILEGES = List[Literal["student"]]

class User(BaseModel):
    edbo_id: int
    email: EmailStr | None = None
    phone_number: str | None = None
    first_name: str
    middle_name: str
    last_name: str 
    age: int
    date_of_birth: str
    role: ROLE
    privileges: PRIVILEGES
    # password: str = Field(..., min_length=8, max_length=16)

# class User()
class UserCreate(User):
    password: str = Field(..., min_length=8, max_length=16)

class UserDelete(BaseModel):
    role: ROLE
    edbo_id: int

class UserPrivate(BaseModel):
    edbo_id: int
    name: str
    email: EmailStr | None = None
    password: str

class UserDB(MongoDB):
    DATABASE_NAME: str
    COLLECTION_NAME: str