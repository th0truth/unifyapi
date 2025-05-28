from typing import Annotated, Optional, List
from fastapi import (
    HTTPException,
    APIRouter,
    status,
    Security,
    Depends,
    Path,
    Body,
    Query
)
from datetime import datetime
import uuid

from core.db import MongoClient

from core.schemas.student import StudentBase
from core.schemas.teacher import TeacherBase
from core.schemas.schedule import (
    ScheduleBase,
    ScheduleCreate
)
from api.dependencies import (
    get_mongo_client,
    get_current_user
)
import crud

router = APIRouter(tags=["Schedule"])

async def get_user_schedule(
        mongo: MongoClient,
        *,
        student: StudentBase,
        schedule_list: list
    ) -> dict:

    grade_db = mongo.get_database("grades")
    grades_doc = await crud.get_grades(grade_db, edbo_id=student.edbo_id, group=student.group)
    user_db = mongo.get_database("users")
    collection = user_db.get_collection("teachers")
    for lesson in schedule_list:
        teacher = await collection.find_one({"edbo_id": lesson.pop("teacher_edbo")})
        lesson.update(
            {"teacher": TeacherBase(**teacher).model_dump(),
             "grade": grades_doc.get(lesson["name"], {}).get(lesson["date"])}
        )
    return schedule_list

@router.get("/my",
    response_model=list[ScheduleBase],
    response_model_exclude_none=True)
async def read_my_schedule(
        user: Annotated[dict, Security(get_current_user, scopes=["student", "teacher"])],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Return the schedule for the current user. 
    """
    schedule_db = mongo.get_database("schedule")
    role = user.get("role")
    match role:
        case "students":
            student = StudentBase(**user)
            collection = schedule_db.get_collection(student.group)
            schedule_list = await collection.find({"group": student.group}).to_list()
            schedule = await get_user_schedule(mongo, student=student, schedule_list=schedule_list)
            return schedule
        case "teachers":
            for name in await schedule_db.list_collection_names():
                collection = schedule_db.get_collection(name) 
                schedule = await collection.find({"teacher_edbo": user["edbo_id"]}).to_list()
                if schedule: break
            return schedule

@router.get("/{group}",
    response_model=List[ScheduleBase],
    response_model_exclude_none=True,                
    dependencies=[Security(get_current_user, scopes=["teacher", "admin"])])
async def read_group_schedule(
        group: Annotated[str, Path],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Return the schedule for the given group. 
    """
    schedule_db = mongo.get_database("schedule")
    collection = schedule_db.get_collection(group)
    schedule = await collection.find().to_list()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group schedule not found."
        )
    return schedule

@router.get("/{group}/{id}",
    response_model=ScheduleBase,
    response_model_exclude_none=True,
    dependencies=[Security(get_current_user, scopes=["teacher", "admin"])])
async def read_schedule_by_id(
        group: Annotated[str, Path],
        id: Annotated[str, Path],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Return the schedule for the given group with a unique id. 
    """
    schedule_db = mongo.get_database("schedule")
    collection = schedule_db.get_collection(group)
    lesson = await collection.find_one({"lesson_id": id})
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found."
        )
    return lesson

@router.post("/create")
async def create_schedule(
    schedule_create: Annotated[ScheduleCreate, Body],
    user: Annotated[dict, Security(get_current_user, scopes=["teacher"])],
    mongo: Annotated[MongoClient, Depends(get_mongo_client)],
    date: Annotated[Optional[str], Query] = None,
):
    """
    Create a schedule for the group.
    """
    teacher = TeacherBase(**user)
    group_db = mongo.get_database("groups")
    for _name in await group_db.list_collection_names():
        collection = group_db.get_collection(_name)
        group = await collection.find_one({"group": schedule_create.group})
        if group: break
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The group not found."
        )
    if schedule_create.name not in teacher.disciplines:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this discipline."
        )

    schedule_db = mongo.get_database("schedule")
    collection = schedule_db.get_collection(schedule_create.group)
    await collection.insert_one(
        {
            "lesson_id": str(uuid.uuid4()),
            "teacher_edbo": teacher.edbo_id,
            "date": date if date else datetime.now().strftime("%d-%m-%Y"),
            **schedule_create.model_dump()
        }
    )
    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="Lesson created successfully."
    )