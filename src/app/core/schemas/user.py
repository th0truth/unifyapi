from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Literal, List

from core.db.database import MongoDB

class User(BaseModel):
    edbo_id: int
    first_name: str
    middle_name: str
    last_name: str 
    date_of_birth: str
    phone_number: List[int]
    role: Literal["students", "lecturers", "admins"] = "students"
    scopes: list
    password: str = Field(..., min_length=8, max_length=16)

class UserCreate(User):
    acc_date: datetime
    
class UserUpdate(BaseModel):
    email: EmailStr | None = None

class UserDelete(BaseModel):
    edbo_id: int
    email: EmailStr | None = None

class UserPublic(BaseModel):
    edbo_id: int
    first_name: str
    middle_name: str
    last_name: str
    role: str

class UserPrivate(BaseModel):
    edbo_id: int
    first_name: str
    middle_name: str
    last_name: str
    role: str
    scopes: list
    email: EmailStr | None = None
    password: str

class UserDB(MongoDB):
    DATABASE_NAME: str
    COLLECTION_NAME: str