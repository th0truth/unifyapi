from datetime import datetime
from fastapi import (
    APIRouter,
    UploadFile,
    Security,
    Depends,
    Query,
    Body
)
import uuid

from core.schemas.user import (
    UserDB,
    ROLE
)
from core.schemas.teacher import Teacher
from core.schemas.schedule import (
    Schedule,
    ScheduleCreate,
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
    teacher = Teacher(**user).model_dump()
    return teacher

@router.get("/my", response_model=list[Schedule])
async def read_my_schedule(user: dict = Depends(deps.get_current_user)):
    """
        Return the schedule for the current user. 
    """
    role: ROLE = user.get("role")
    match role:
        case "students":
            ScheduleDB.COLLECTION_NAME = user.get("group")
            schedule = await ScheduleDB.find_many({"group": user.get("group")})
            grades = await crud.get_grades(edbo_id=user.get("edbo_id"), group=user.get("group"))
            for lesson in schedule:
                lesson.update(
                    {"teacher": await get_teacher_info(lesson=lesson),
                     "grade": grades.get(lesson["name"], {}).get(lesson["date"], None) if grades else None})
        case _:
            collections = await ScheduleDB.get_collections()
            for collection in collections:
                ScheduleDB.COLLECTION_NAME = collection
                schedule = await ScheduleDB.find_many({"teacher_edbo": user.get("edbo_id")})
                if schedule:
                    break
    if not schedule:
        raise exc.NOT_FOUND(
            detail="Your schedule not found."
        )
    return schedule

@router.get("/{group}", response_model=list[Schedule],
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_group_schedule(
        group: str,
        skip: int | None = None,
        length: int | None = None,
    ):
    """
        Return the schedule for the given group. 
    """
    ScheduleDB.COLLECTION_NAME = group
    schedule = await ScheduleDB.find_many(skip=skip, length=length)
    if not schedule:
        raise exc.NOT_FOUND(detail="Group schedule not found.")
    for lesson in schedule:
        lesson.update({"teacher": await get_teacher_info(lesson=lesson)})
    return schedule

@router.get("/{group}/{id}", response_model=Schedule,
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_schedule_by_id(
        group: str,
        id: str,
    ):
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
async def create_schedule(
    body: ScheduleCreate = Body(),
    file: UploadFile | None = None, # fix this issue
    teacher_edbo: int | None = Query(None),
    date: str | None = Query(None),                
    user: dict = Security(
        deps.get_current_user, scopes=["teacher", "admin"]),
):
    """
        Create a schedule for the group.
    """

    # search given group
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

    # add attachment to lesson
    if file:
        f_bytes = await file.read()
        file_id = await ScheduleDB.upload_file(
            file.filename, f_bytes, file.content_type)
    
    await ScheduleDB.create(
        {"date": date if date else datetime.now().strftime("%d-%m-%Y"),
        "teacher_edbo": teacher_edbo,
        "lesson_id": str(uuid.uuid4()),
        "file_id": file_id,
            **body.model_dump()})
    raise exc.CREATED(
        detail="The lesson has been created successfully."
    )

@router.post("/upload/file", dependencies=[Depends(deps.get_current_user)])
async def create_upload_file(file: UploadFile):
    """
        Upload file for schedule.
    """
    f_bytes = await file.read() 
    await ScheduleDB.upload_file(
        file.filename, f_bytes, file.content_type)

# @router.get("/download/{filename}")
# async def download_file(filename: str):
    # pass

@router.delete("/delete/file")
async def delete_file(filename: str = Body()):
    """
        Delete a file by `filename`.    
    """
    ScheduleDB.COLLECTION_NAME = "fs.files"
    file = await ScheduleDB.find_by({"filename": filename})
    if not file:
        raise exc.NOT_FOUND(
            detail="File not found.")
    file_id = file.get("_id")
    await ScheduleDB.delete_file(file_id=file_id)
    raise exc.OK(
        detail="File has been deleted successfully."
    )

# @router.patch("/update")
# async def update_schedule(
#         group: str,
#         date: str = Query(),
#         body: dict = Body(),
#         user: dict = Security(deps.get_current_user, scopes=["teacher", "admin"])
#     ):
    
#     groups = await ScheduleDB.get_collections()
#     if group not in groups:
#         raise exc.NOT_FOUND(
#             detail="Group not found."
#         )

#     ScheduleDB.COLLECTION_NAME = group

#     role: ROLE = user.get("role")
#     match role:
#         case "teachers":
#             lesson = await ScheduleDB.find_by({"date": date})
#             if not lesson:
#                 raise exc.NOT_FOUND(
#                     detail="Lesson not found for this date."
#                 )
#             await Schedule.

    # role: ROLE = user.get("role")
    # match role:
    #     case "teachers":
    #         lesson = await ScheduleDB.find_by({"date": date})
    #         print(lesson)
    #         if not lesson:
    #             raise exc.NOT_FOUND(
    #                 detail="Your lesson not found."
    #             )
    #         await ScheduleDB.update_one(
    #             filter={""})

    #             filter={""},
    #             update=update
    #         )
    #         raise exc.OK(
    #             detail="The user schedule has been updated.")

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