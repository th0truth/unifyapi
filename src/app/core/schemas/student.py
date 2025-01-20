from pydantic import BaseModel, Field, EmailStr
from .user import UserCreate

class StudentCreate(UserCreate):
    class_name: str = Field(..., min_length=3)
    role: str = "students"

class StudentPublic(BaseModel):
    role: str | None = None
    edbo_id: int
    name: str

class StudentPrivate(BaseModel):
    edbo_id: int
    name: str
    email: EmailStr | None = None
    password: str