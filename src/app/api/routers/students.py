from typing import Annotated, Optional, List
from fastapi import (
    HTTPException,
    APIRouter,
    status,
    Security,
    Depends,
    Query,
    Path,
    Body
)

from core.db import MongoClient

from core.schemas.student import (
    StudentBase,
    StudentCreate
)
from core.schemas.grade import GradeBase
from api.dependencies import (
    get_mongo_client,
    get_current_user
)
import crud

router = APIRouter(tags=["Students"])

@router.post("/create",
    dependencies=[Security(get_current_user, scopes=["admin"])])
async def create_student(
        student_create: Annotated[StudentCreate, Body],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)] 
    ):
    """
    Create a student account.
    """
    group_db = mongo.get_database("groups")
    collection = group_db.get_collection(student_create.degree)
    group = await collection.find_one({"group": student_create.group})
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The student's group not found."
        )
    user_db = mongo.get_database("users")
    return await crud.create_user(user_db, user=student_create)

@router.post("/group/{name}/all", response_model=List[StudentBase],
    dependencies=[Security(get_current_user, scopes=["teacher", "admin"])])
async def read_students(
        name: Annotated[str, Path],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ) -> List[StudentBase]:
    """
    Return a list of all existing students from the given group.
    """
    user_db = mongo.get_database("users")
    return await crud.read_users(user_db, role="students", filter="group", value=name)

@router.post("/grades/my")
async def get_current_student_grades(
        body: Annotated[GradeBase, Body],
        student: Annotated[dict, Security(get_current_user, scopes=["student"])],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Fetch the current student grades by `subject`.    
    """
    grade_db = mongo.get_database("grades")
    return await crud.get_grades(grade_db, edbo_id=student["edbo_id"], group=student["group"], subject=body.subject, date=body.date)

@router.get("/grades/my/all")
async def get_current_student_all_grades(
        student: Annotated[StudentBase, Security(get_current_user, scopes=["student"])],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)],
        date: Annotated[Optional[str], Query] = None
    ):
    """
    Fetch all grades for the current user.
    """
    grade_db = mongo.get_database("grades")
    return await crud.get_grades(grade_db, edbo_id=student["edbo_id"], group=student["group"], date=date)

@router.post("/grades/{edbo_id}",
    response_model_exclude_none = True,
    dependencies=[Security(get_current_user, scopes=["teacher", "admin"])])
async def get_student_grades(
        edbo_id: Annotated[int, Path],
        body: Annotated[GradeBase, Body],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)],
    ):
    """
    Return the specified student's subject grades.
    """
    user_db = mongo.get_database("users")
    collection = user_db.get_collection("students")
    student = StudentBase(**await collection.find_one({"edbo_id": edbo_id}))
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found."
        )
    grade_db = mongo.get_database("grades")
    return await crud.get_grades(grade_db, edbo_id=edbo_id, group=student.group, subject=body.subject, date=body.date)

@router.get("/grades/{edbo_id}/all",
    dependencies=[Security(get_current_user, scopes=["teacher", "admin"])])
async def get_student_all_grades(
        edbo_id: Annotated[int, Path],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)],
        date: Annotated[Optional[str], Query] = None,
    ):
    """
    Return all subject grades. 
    """
    user_db = mongo.get_database("users")
    collection = user_db.get_collection("students")
    student = StudentBase(**await collection.find_one({"edbo_id": edbo_id}))
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found."
        )
    grade_db = mongo.get_database("grades")
    return await crud.get_grades(grade_db, edbo_id=edbo_id, group=student.group, date=date)