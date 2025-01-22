from core.db.database import MongoDB
from pydantic import BaseModel

class ScheduleDB(MongoDB):
    DATABASE_NAME: str = "timetable"
    COLLECTION_NAME: str = "IPZ-12"