from fastapi import APIRouter

from core.schemas.schedule import ScheduleDB

router = APIRouter(tags="Schedule")

ScheduleDB.DATABASE_NAME = "timetable"

