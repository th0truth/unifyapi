from pydantic import BaseModel

from core.db.database import MongoDB 

class Grade(BaseModel):
    subject: str

class SetGrade(BaseModel):
    subject: str
    grade: int

class GradeDB(MongoDB):
    DATABASE_NAME = "grades"