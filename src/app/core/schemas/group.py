from core.db.database import MongoDB

from pydantic import BaseModel

class Group(BaseModel):
    group: str
    degree: str
    course: int
    disciplines: dict
    class_teacher_edbo: int
    specialty: str

class GroupDelete(BaseModel):
    group: str

class GroupDB(MongoDB):
    DATABASE_NAME: str = "users"
    COLLECTION_NAME: str = "groups"    