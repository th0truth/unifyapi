from typing import List 
from fastapi import APIRouter

from core.schemas.schedule import (
    Schedule,
    ScheduleDB
)

router = APIRouter(tags=["Schedule"])

ScheduleDB.DATABASE_NAME = "schedule"

@router.get("/{group}", response_model=List[Schedule])
async def read_group_schedule(group: str):
    ScheduleDB.COLLECTION_NAME = group
    return await ScheduleDB.find_all()

@router.get("/{group}/{id}", response_model=Schedule)
async def read_schedule_by_id(group: str, id: str):
    ScheduleDB.COLLECTION_NAME = group
    return await ScheduleDB.find_by({"lesson_id": id})