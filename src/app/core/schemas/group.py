from pydantic import BaseModel
from core.db.database import MongoDB

from .user import DEGREE
from .teacher import Teacher

class Group(BaseModel):
    degree: str
    course: int
    group: str
    specialty: str
    disciplines: list
    class_teacher: Teacher | None = None

class GroupDelete(BaseModel):
    group: str

class GroupDB(MongoDB):
    DATABASE_NAME: str = "groups"
    COLLECTION_NAME: str    