from datetime import datetime
from pydantic import Field

from .user import UserBase
from .etc import PASSWORDstr

class TeacherBase(UserBase):
    disciplines: list
    specialities: list

class TeacherCreate(TeacherBase):
    role: str = "teachers"
    acc_date: datetime
    password: PASSWORDstr