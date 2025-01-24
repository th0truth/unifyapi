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
    group: str

class ScheduleDB(MongoDB):
    DATABASE_NAME: str = "schedules"
    COLLECTION_NAME: str = "ipz-12"