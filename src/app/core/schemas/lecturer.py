from pydantic import BaseModel
from .user import UserCreate

class LecturerCreate(UserCreate):
    disciplines: list
    specialities: list