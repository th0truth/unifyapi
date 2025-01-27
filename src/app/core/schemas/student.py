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
    role: str
    edbo_id: int
    first_name: str
    middle_name: str
    last_name: str
    group: str

class StudentPrivate(BaseModel):
    edbo_id: int
    first_name: str
    middle_name: str
    last_name: str
    course: int
    group: str
    email: EmailStr | None = None
    password: str