from pydantic import BaseModel
from core.db.database import MongoDB

from .user import DEGREE
from .teacher import Teacher

class Group(BaseModel):
    degree: str
    course: int
    group: str
    specialty: str
    # disciplines: dict | None = None
    class_teacher: Teacher | None = None

class GroupDelete(BaseModel):
    group: str

class GroupDB(MongoDB):
    DATABASE_NAME = "groups"