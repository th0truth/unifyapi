from pydantic import BaseModel

from core.db.database import MongoDB
from .teacher import Teacher 

class Group(BaseModel):
    degree: str
    course: int
    group: str
    specialty: str
    disciplines: list | dict
    class_teacher: Teacher | None = None

class GroupDelete(BaseModel):
    group: str

class GroupDB(MongoDB):
    DATABASE_NAME: str = "users"
    COLLECTION_NAME: str = "groups"    