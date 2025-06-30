from typing import Annotated, List
from fastapi import (
  HTTPException,
  APIRouter,
  status,
  Security,
  Depends,
  Path,
  Body
)
from uuid import uuid4

from core.db import MongoClient

from core.schemas.student import StudentBase
from core.schemas.teacher import TeacherBase
from core.schemas.schedule import (
  ScheduleBase,
  ScheduleCreate,
  SchedulePrivate
)
from api.dependencies import (
  get_mongo_client,
  get_current_user
)
import crud

router = APIRouter(tags=["Schedule"])

@router.get("/my",
  status_code=status.HTTP_200_OK,
  response_model=list[SchedulePrivate],
  response_model_exclude_none=True)
async def get_current_user_schedule(
  user: Annotated[dict, Security(get_current_user, scopes=["student", "teacher"])],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)]
):
  """
  Fetch a schedule for the current user. 
  """
  schedule_db = mongo.get_database("schedule")
  match user.get("role"):
    case "students":
      student = StudentBase.model_validate(user) 
      collection = schedule_db.get_collection(student.group)
      schedule = await collection.find().to_list()

      grades_db = mongo.get_database("grades")
      grades_doc = await crud.get_grades(grades_db, edbo_id=student.edbo_id, group=student.group)
      
      user_db = mongo.get_database("users")
      collection = user_db.get_collection("teachers")
      for subject in schedule:
        teacher = await collection.find_one({"edbo_id": subject.pop("teacher_edbo")})
        subject.update(
          {"teacher": TeacherBase.model_validate(teacher).model_dump(),
           "grade": grades_doc.get(subject["subject"], {}).get(subject["date"])})
      return schedule

    case "teachers":
      teacher = TeacherBase.model_validate(user)
      for group in await schedule_db.list_collection_names():
        collection = schedule_db.get_collection(group)
        schedule = await collection.find({"teacher_edbo": teacher.edbo_id}).to_list()
        if schedule: break
      return schedule

@router.get("/{group}",
  status_code=status.HTTP_200_OK,
  response_model=List[ScheduleBase],
  response_model_exclude_none=True,                
  dependencies=[Security(get_current_user, scopes=["teacher", "admin"])])
async def get_schedule_by_group(
  group: Annotated[str, Path()],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)]
):
  """
  Fetch a schedule for the given group. 
  """
  schedule_db = mongo.get_database("schedule")
  collection = schedule_db.get_collection(group)
  schedule = await collection.find().to_list()
  return schedule

@router.get("/{group}/{id}", 
  status_code=status.HTTP_200_OK,
  response_model=ScheduleBase,
  response_model_exclude_none=True,
  dependencies=[Security(get_current_user, scopes=["teacher", "admin"])])
async def get_schedule_by_id(
  group: Annotated[str, Path()],
  id: Annotated[str, Path()],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)]
):
  """
  Fetch the schedule for the given group with a id.
  """
  schedule_db = mongo.get_database("schedule")
  collection = schedule_db.get_collection(group)
  subject = await collection.find_one({"subject_id": id})
  if not subject:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Subject not found."
    )
  return subject

@router.post("/create",
  status_code=status.HTTP_201_CREATED,
  response_model=ScheduleBase,
  response_model_exclude_none=True)
async def create_schedule(
  schedule: Annotated[ScheduleCreate, Body()],
  user: Annotated[dict, Security(get_current_user, scopes=["teacher"])],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)],
):
  """
  Create a schedule for the given group.
  """
  teacher = TeacherBase.model_validate(user)
  groups_db = mongo.get_database("groups")

  for degree in await groups_db.list_collection_names():
    collection = groups_db.get_collection(degree)
    group = await collection.find_one({"group": schedule.group})
    if group: break
  
  if not group:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Given group not found."
    )
  
  if schedule.subject not in teacher.disciplines:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="You don't have access to this discipline."
    )

  schedule_db = mongo.get_database("schedule")
  collection = schedule_db.get_collection(schedule.group)
  
  schedule_private = SchedulePrivate(
    **schedule.model_dump(),
    teacher_edbo=teacher.edbo_id,
    subject_id=str(uuid4())
  )

  await collection.insert_one(
    schedule_private.model_dump()
  )

  return schedule

@router.patch("/update",
  status_code=status.HTTP_200_OK)
async def update_schedule(
  group: Annotated[str, Path()],
  id: Annotated[str, Path()],
):
  """
  Update 
  """


@router.delete("/delete")
async def delete_schedule():
  pass