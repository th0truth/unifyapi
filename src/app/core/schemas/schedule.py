from core.db.database import MongoDB

class ScheduleDB(MongoDB):
    DATABASE_NAME: str = "schedules"
    COLLECTION_NAME: str = "ipz-12"