from pydantic import BaseModel
from .user import User, UserCreate

class Student(User):
    role: str = "students"
    scopes: list = ["students"]
    course: int
    group: str
    class_teacher_edbo: int

class StudentCreate(UserCreate):
    role: str = "students"
    scopes: list = ["students"]
    speciality: str
    course: int
    group: str
    start_of_study: str
    complete_of_study: str
    class_teacher_edbo: int