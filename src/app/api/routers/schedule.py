from fastapi import (
    APIRouter,
    Security,
    Depends,
    Query,
    Body
)

from datetime import datetime
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
import crud

router = APIRouter(tags=["Schedule"])

async def get_teacher_info(lesson: dict) -> dict:
    UserDB.COLLECTION_NAME = "teachers"
    edbo_id = lesson.pop("teacher_edbo")
    user = await UserDB.find_by({"edbo_id": edbo_id})
    return ScheduleTeacher(**user).model_dump()

@router.get("/my", response_model=list[Schedule])
async def read_my_schedule(user: dict = Security(deps.get_current_user, scopes=["student", "teacher"])):
    """
        Return the schedule for me. 
    """

    role: ROLE = user.get("role")
    match role:
        case "students":
            group: str = user.get("group")
            ScheduleDB.COLLECTION_NAME = group
            schedule = await ScheduleDB.find_many(filter="group", value=group)
            grades = await crud.get_grades(edbo_id=user.get("edbo_id"))
            for lesson in schedule:
                    name, date = lesson["name"], lesson["date"]
                    lesson.update({"teacher": await get_teacher_info(lesson=lesson)})    
                    try:
                        lesson.update({"grade": grades[name][date]})
                    except KeyError:
                        continue
        case "teachers":
            collections = await ScheduleDB.get_collections()
            for collection in collections:
                ScheduleDB.COLLECTION_NAME = collection                
                schedule = await ScheduleDB.find_many(
                    filter="teacher_edbo", value=user.get("edbo_id"))
                for lesson in schedule:
                    await get_teacher_info(lesson=lesson)
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

@router.post("/create")
async def create_schedule(body: ScheduleCreate = Body(), 
    user: dict = Security(deps.get_current_user, scopes=["teacher", "admin"]),
    teacher_edbo: int | None = Query(None), date: str | None = Query(None)):                
    """
        Create a schedule for the group.
    """

    groups = await ScheduleDB.get_collections()    
    if body.group not in groups:
        raise exc.NOT_FOUND(
            detail="The group not found.")
    ScheduleDB.COLLECTION_NAME = body.group

    role: ROLE = user.get("role")
    match role:
        case "teachers":
            if body.name not in user.get("disciplines"):
                raise exc.FORBIDDEN(
                    detail="You don't have access to this discipline."
                )
        case "admins":
            if not teacher_edbo:
                raise exc.CONFLICT(
                    detail="The `teacher_edbo` field must be filled in."
                )
            UserDB.COLLECTION_NAME = "teachers"
            teacher = await UserDB.find_by({"edbo_id": teacher_edbo})
            if not teacher:
                raise exc.NOT_FOUND("Teacher not found.")
            disciplines = teacher.get("disciplines")
            if body.name not in disciplines:
                raise exc.FORBIDDEN(
                    detail="This teacher don't have access to this discipine."
                )

    await ScheduleDB.create(
        {"date": date if date else datetime.now().strftime("%d-%m-%Y"),
        "teacher_edbo": teacher_edbo,
        "lesson_id": str(uuid.uuid4()),
            **body.model_dump()})
    raise exc.CREATED(
        detail="The lesson has been created successfully."
    )

@router.patch("/update/{group}", deprecated=True)
async def update_schedule(group: str, date: str | None = None, update: dict = Body(),
    user: dict = Security(deps.get_current_user, scopes=["teacher", "admin"])):
    """
    
    """
    groups = await ScheduleDB.get_collections()
    if group not in groups:
        raise exc.NOT_FOUND(
            detail="The given group not found.")    
    
    ScheduleDB.COLLECTION_NAME = group
    role: ROLE = user.get("role")
    match role:
        case "teachers":
            # schedule = await ScheduleDB.find_by({"": date})
            # if not schedule:
                # raise exc.NOT_FOUND(
                    # ""
                # )
            await ScheduleDB.update_one(

                filter={""},
                update=update
            )
            raise exc.OK(
                detail="The user schedule has been updated.")

    # ScheduleDB.COLLECTION_NAME = group
    # await ScheduleDB.update_one(filter={"date": date}, update=update)
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