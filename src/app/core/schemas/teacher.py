from pydantic import BaseModel, Field, EmailStr
from core.db.database import MongoDB

class TeacherDB(MongoDB):
    DATABASE_NAME = "college"
    COLLECTION_NAME = "teacher"