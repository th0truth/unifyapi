from fastapi import (
    APIRouter,
    Security,
    Depends,
)

from core.schemas.user import UserDB, ROLE
from core.schemas.schedule import (
    Schedule,
    ScheduleTeacher,
    ScheduleDB
)

from core import exc
import api.deps as deps

router = APIRouter(tags=["Schedule"])

async def get_teacher_info(lesson: dict) -> dict:
    UserDB.COLLECTION_NAME = "teachers"
    edbo_id: int = lesson.pop("teacher_edbo")
    user = await UserDB.find_by({"edbo_id": edbo_id})
    return ScheduleTeacher(**user).model_dump()

@router.get("/my", response_model=list[Schedule])
async def read_my_schedule(user: dict = Depends(deps.get_current_user)):
    """
        Return the schedule for me. 
    """

    role: ROLE = user.get("role")
    match role:
        case "students":
            group: str = user.get("group")
            ScheduleDB.COLLECTION_NAME = group
            schedule = await ScheduleDB.find_many(filter="group", value=group)
            for lesson in schedule:
                lesson.update(
                    {"teacher": await get_teacher_info(lesson=lesson)})
        case "teachers":
            collections = await ScheduleDB.get_collections()
            for collection in collections:
                ScheduleDB.COLLECTION_NAME = collection                
                schedule = await ScheduleDB.find_many(
                    filter="teacher_edbo", value=user.get("edbo_id"))
                for lesson in schedule:
                    await get_teacher_info(lesson=lesson)
        case _:
            raise exc.INTERNAL_SERVER_ERROR()
    return schedule

@router.get("/{group}", response_model=list[Schedule],
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_group_schedule(group: str, skip: int | None = None, length: int | None = None):
    """
        Return the schedule for the given group. 
    """
    
    ScheduleDB.COLLECTION_NAME = group
    schedule = await ScheduleDB.find_many(skip=skip, length=length)
    if not schedule:
        raise exc.NOT_FOUND(detail="Group schedule not found.")
    for lesson in schedule:
        await get_teacher_info(lesson=lesson)
    return schedule

@router.get("/{group}/{id}", response_model=Schedule,
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_schedule_by_id(group: str, id: str):
    """
        Return the schedule for the given group with a unique id. 
    """
    
    ScheduleDB.COLLECTION_NAME = group
    lesson = await ScheduleDB.find_by({"lesson_id": id})
    if not lesson:
        raise exc.NOT_FOUND(detail="Lesson not found.")
    await get_teacher_info(lesson=lesson)
    return lesson
# 
# @router.patch("/update/{group}",
            #   dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
# async def update_schedule(group: str, date: str | None = None, update: dict = Body()):
    # groups = await ScheduleDB.get_collections()
    # if group not in groups:
        # raise exc.NOT_FOUND(
            # detail="The given group not found.")    
    # ScheduleDB.COLLECTION_NAME = group
    # await ScheduleDB.update_one({"time": date}, update=update)
    # raise exc.OK(
        # detail="The user schedule has been updated.")
# 
# @router.patch("/update/{group}/all",
            #   dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
# async def update_entire_schedule(group: str, filter: dict, data: dict):
    # """
        # Update users data.
    # """
# 
    # groups = await ScheduleDB.get_collections()
    # if group not in groups:
        # raise exc.NOT_FOUND(
            # detail="The given group not found.")
    # ScheduleDB.COLLECTION_NAME = group
    # await ScheduleDB.update_many(filter=filter, data=data)