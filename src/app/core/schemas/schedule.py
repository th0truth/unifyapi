from pydantic import BaseModel

from core.db.database import MongoDB

class Schedule(BaseModel):
    name: str
    lesson_id: str
    position: int
    classroom: int
    time: str
    topic: str
    homework: str
    teacher_edbo: int
    teacher: dict
    group: str

class ScheduleTeacher(BaseModel):
    edbo_id: int
    first_name: str
    middle_name: str
    last_name: str
    specialities: list
    disciplines: list

class ScheduleDB(MongoDB):
    DATABASE_NAME: str = "schedules"
    COLLECTION_NAME: str = "ipz-12"