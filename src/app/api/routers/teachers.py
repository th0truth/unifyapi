from typing import Annotated
from fastapi import (
    HTTPException,
    APIRouter,
    status,
    Security,
    Depends,
    Path,
    Body
)

from core.db import MongoClient

from core.schemas.student import StudentBase
from core.schemas.teacher import TeacherCreate
from core.schemas.grade import SetGrade
from api.dependencies import (
    get_mongo_client,
    get_current_user
)
import crud

router = APIRouter(tags=["Teachers"])

@router.post("/create",
    dependencies=[Security(get_current_user, scopes=["admin"])])
async def create_teacher(
        teacher_create: Annotated[TeacherCreate, Body],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Create a teacher account.
    """
    user_db = mongo.get_database("users")
    return await crud.create_user(user_db, user=teacher_create)

@router.patch("/set-grade/{edbo_id}")
async def set_grade(
        edbo_id: Annotated[int, Path],
        body: Annotated[SetGrade, Body],
        teacher: Annotated[dict, Security(get_current_user, scopes=["teacher"])],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Set given student grade.
    """
    if body.subject not in teacher["disciplines"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this discipline."
        )
    user_db = mongo.get_database("users")
    collection = user_db.get_collection("students")
    student = StudentBase(**await collection.find_one({"edbo_id": edbo_id}))
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found."
        )
    grade_db = mongo.get_database("grades")
    collection = grade_db.get_collection(student.group)
    await collection.update_one(
        filter={"edbo_id": edbo_id},
        update={
            "$set": {f"disciplines.{body.subject}.{body.date}": body.grade}
        }
    )
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="Student grade successfully added."
    )