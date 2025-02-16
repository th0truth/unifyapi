from pydantic import BaseModel, HttpUrl, Field
from .user import User, UserCreate

class Teacher(User):
    disciplines: list
    specialities: list

class TeacherCreate(UserCreate):
    role: str = "teachers"
    disciplines: list
    specialities: list

class TeacherCount(BaseModel):
    specialities: list