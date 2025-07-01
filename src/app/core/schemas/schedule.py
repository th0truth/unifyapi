from pydantic import BaseModel
from typing import Optional

from .teacher import TeacherBase
from bson import ObjectId
from typing import Any

class ScheduleBase(BaseModel):
  subject: str
  position: int
  classroom: int
  date: str
  topic: str
  homework: str

class ScheduleCreate(ScheduleBase):
  group: str
  date: str

class SchedulePrivate(ScheduleCreate):
  teacher: Optional[TeacherBase] = None 
  teacher_edbo: Optional[int] = None
  grade: Optional[int] = None
  lesson_id: str