from pydantic import BaseModel

from core.db.database import MongoDB 

class Grade(BaseModel):
    subject: str

class GradeDB(MongoDB):
    DATABASE_NAME: str = "grades"
    COLLECTION_NAME: str