from typing import Optional, Literal, List
from datetime import datetime
from pydantic import (
    BaseModel,
    EmailStr,
)

from .etc import PASSWORDstr

ROLE = Literal["students", "teachers", "admins"]
DEGREE = Literal["bachelor", "skilled_worker"] 

class UserBase(BaseModel):
  edbo_id: int
  first_name: str
  middle_name: str
  last_name: str 
  date_of_birth: str
  role: ROLE

class UserPrivate(UserBase):
    acc_date: datetime
    email: Optional[EmailStr] = None
    phone_number: Optional[List[int]] = None
    password: Optional[str] = None
    scopes: list

class UserCreate(UserBase):
    acc_date: datetime
    password: PASSWORDstr

class UserUpdate(UserBase):
    scopes: list

class UserUpdateEmail(BaseModel):
    email: Optional[EmailStr] = None
    password: str