from typing import List
from fastapi import (
    APIRouter,
    Security,
)

from core.schemas.user import UserDB
from core.schemas.schedule import (
    Schedule,
    ScheduleTeacher,
    ScheduleDB
)
from core import exc
import api.deps as deps

router = APIRouter(tags=["Schedule"])

ScheduleDB.DATABASE_NAME = "schedule"

@router.get("/{group}", response_model=List[Schedule],
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_group_schedule(group: str, skip: int | None = None, length: int | None = None):
    ScheduleDB.COLLECTION_NAME = group
    schedule = await ScheduleDB.find_many(skip=skip, length=length)
    if not schedule:
        raise exc.NOT_FOUND(detail="Group schedule not found.")
    UserDB.COLLECTION_NAME = "teachers"
    for lesson in schedule:
        edbo_id: int = lesson.get("teacher_edbo")
        user = await UserDB.find_by({"edbo_id": edbo_id}) 
        lesson.update({"teacher": ScheduleTeacher(**user).model_dump()})
    return schedule

@router.get("/{group}/{id}", response_model=Schedule,
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_schedule_by_id(group: str, id: str):
    ScheduleDB.COLLECTION_NAME = group
    schedule = await ScheduleDB.find_by({"lesson_id": id})
    if not schedule:
        raise exc.NOT_FOUND(detail="Group schedule not found.")
    return schedule

# @router.get("/my", response_model=[Schedule])
# async def read_my_schedule(student: StudentPublic = Security(deps.get_current_user, scopes=["student"])):
#     """
#         Return 
#     """
#     ScheduleDB.COLLECTION_NAME = student.get("group")
#     return await ScheduleDB.find_many(filter="group", value=student.get("group"))