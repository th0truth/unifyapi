from typing import List
from fastapi import (
    APIRouter,
    Security,
    Depends,
    Body
)
import uuid

from core.schemas.user import UserDB, ROLE
from core.schemas.schedule import (
    Schedule,
    ScheduleCreate,
    ScheduleTeacher,
    ScheduleDB
)
from core import exc
import api.deps as deps

router = APIRouter(tags=["Schedule"])

ScheduleDB.DATABASE_NAME = "schedule"

async def get_teacher_info(lesson: dict):
    UserDB.COLLECTION_NAME = "teachers"
    edbo_id: int = lesson.pop("teacher_edbo")
    user = await UserDB.find_by({"edbo_id": edbo_id})
    lesson.update({"teacher": ScheduleTeacher(**user).model_dump()})

@router.get("/my", response_model=List[Schedule])
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
                await get_teacher_info(lesson=lesson)
        case "teachers":
            collections = await ScheduleDB.get_collections()
            for collection in collections:
                ScheduleDB.COLLECTION_NAME = collection                
                schedule = await ScheduleDB.find_many(
                    filter="teacher_edbo", value=user.get("edbo_id"))
                for lesson in schedule:
                    await get_teacher_info(lesson=lesson)
        case _:
            raise exc.UNPROCESSABLE_CONTENT()
    return schedule                

@router.get("/{group}", response_model=List[Schedule],
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

@router.post("/create/{group}")
async def create_lesson(group: str, body: ScheduleCreate = Body(), 
    user: dict = Security(deps.get_current_user, scopes=["teacher", "admin"])):                   
    """
        Create a lesson.
    """

    ScheduleDB.COLLECTION_NAME = group
    await ScheduleDB.create(
        {"teacher_edbo": user.get("edbo_id"),
        "group": group,
        "lesson_id": str(uuid.uuid4()),
         **body.model_dump()})
    raise exc.CREATED(
        detail="The lesson has been created successfully."
    )