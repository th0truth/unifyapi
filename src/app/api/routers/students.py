from typing import List, Dict, Any
from fastapi import (
    APIRouter,
    Security,
    Body,
)

from core.schemas.user import UserDB
from core.schemas.group import GroupDB
from core.schemas.student import (
    Student,
    StudentCreate,
)

import api.deps as deps
from core import exc
import crud

router = APIRouter(tags=["Students"])

UserDB.COLLECTION_NAME = "students"

@router.post("/create", dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def create_student(student: StudentCreate = Body()):
    """
        Create a student account.
    """
    
    group = await GroupDB.find_by({"group": student.group})
    if not group:
        raise exc.NOT_FOUND("The student's group not found.")
    return await crud.create_user(user=student)

@router.get("/all/{group}", response_model=List[Student],
        dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_students(group: str, skip: int = 0, length: int | None = None) -> List[Student]:
    """
        Return a list of all existing students from the given group.
    """

    return await crud.read_users(role="students", filter="group", value=group, skip=skip, length=length)

@router.get("/all/{group}/count", response_model=int,
           dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def count_students(group: str):
    """
        Return the number of students in the group. 
    """

    count = await crud.count_users(collection="students", filter={"group": group})
    if not count:
        raise exc.NOT_FOUND(detail="There are no students in this group.")
    return count

@router.post("/get/grades", response_model=Dict[str, Any],
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def get_student_grades(edbo_id: int = Body(), lesson: str = Body()):
    """
        Return the specified student's subject grades. 
    """

    UserDB.COLLECTION_NAME = "students"
    user = await UserDB.find_by({"edbo_id": edbo_id})
    if not user:
        raise exc.NOT_FOUND("Student not found.")
    grades = await crud.get_grades(
        student_name=await crud.get_user_fullname(user=user),
        group_name=user.get("group"),
        lesson=lesson
    )
    return grades

@router.post("/all/grades/{edbo_id}", response_model=Dict[str, Any],
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def get_student_all_grades(edbo_id: int):
    """
        Return the specified student's subject grades. 
    """

    UserDB.COLLECTION_NAME = "students"
    user = await UserDB.find_by({"edbo_id": edbo_id})
    if not user:
        raise exc.NOT_FOUND("Student not found.")
    student = Student(**user)
    group = await GroupDB.find_by({"group": student.group})
    if not group:
        raise exc.NOT_FOUND("Group not found")

    disciplines = group.get("disciplines")
    gradebook = {}
    try:
        for discipline in disciplines:
            grades = await crud.get_grades(
                student_name=await crud.get_user_fullname(user=user),
                group=student.group,
                discipline=discipline
            )
            gradebook.update({discipline: grades})
    except:
        raise exc.INTERNAL_SERVER_ERROR(
            detail={"error": "Something went wrong while retrieving grades."})
    print(gradebook)
    return gradebook