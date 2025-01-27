from pydantic import BaseModel
from .user import UserCreate

class TeacherCreate(UserCreate):
    role: str = "teachers"
    disciplines: list
    specialities: list
    groups: list

class TeacherCount(BaseModel):
    specialities: list