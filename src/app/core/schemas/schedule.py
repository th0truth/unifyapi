from pydantic import BaseModel
from core.db.database import MongoDB

class Schedule(BaseModel):
    teacher: dict | None = None
    name: str
    lesson_id: str
    position: int
    classroom: int
    time: str
    topic: str
    homework: str

class ScheduleTeacher(BaseModel):
    edbo_id: int
    first_name: str
    middle_name: str
    last_name: str
    specialities: list
    disciplines: list

class Lesson(BaseModel):
    lesson: str

class LessonCreate(BaseModel):
    group: str
    name: str
    position: int
    classroom: int
    time: str
    topic: str
    homework: str

class ScheduleDB(MongoDB):
    DATABASE_NAME: str = "schedule"
    COLLECTION_NAME: str