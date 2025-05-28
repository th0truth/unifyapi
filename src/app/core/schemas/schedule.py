from pydantic import BaseModel
from typing import Optional

class ScheduleBase(BaseModel):
    teacher: Optional[dict] = None
    name: str
    lesson_id: str
    position: int
    classroom: int
    date: str
    topic: str
    homework: str
    grade: Optional[int] = None

class ScheduleTeacher(BaseModel):
    edbo_id: int
    first_name: str
    middle_name: str
    last_name: str
    specialities: list
    disciplines: list

class ScheduleCreate(BaseModel):
    group: str
    name: str
    position: int
    classroom: int
    topic: str
    homework: str