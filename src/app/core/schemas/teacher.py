from typing import Dict
from pydantic import BaseModel, HttpUrl, Field
from .user import UserCreate

class TeacherCreate(UserCreate):
    role: str = "teachers"
    disciplines: list
    specialities: list
    groups: Dict[str, HttpUrl] = Field(
        description="Group name with Google SpreadSheet URL of subject grades")

class TeacherCount(BaseModel):
    specialities: list

class GradesGroup(BaseModel):
    group: str
    subject: str