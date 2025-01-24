from pydantic import BaseModel, EmailStr
from .user import UserCreate

class StudentCreate(UserCreate):
    role: str = "students"
    scopes: list = ["students"]
    speciality: str
    course: int
    group: str
    start_of_study: str
    complete_of_study: str

class StudentPublic(BaseModel):
    role: str | None = None
    edbo_id: int
    name: str

class StudentPrivate(BaseModel):
    edbo_id: int
    name: str
    email: EmailStr | None = None
    password: str