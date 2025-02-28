from typing import (
    List
)
from fastapi import (
    APIRouter,
    Security,
    Query,
    Body
)

from datetime import datetime

from core.schemas.user import UserDB
from core.schemas.group import GroupDB
from core.schemas.student import (
    Student,
    StudentCreate,
)

from core.schemas.grade import (
    Grade,
    SetGrade,
    GradeDB
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

@router.post("/grades/{edbo_id}",
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def get_student_grades(edbo_id: int, date: str | None = Query(None), body: Grade = Body()):
    """
        Return the specified student's subject grades.
    """

    student = await UserDB.find_by({"edbo_id": edbo_id})
    if not student:
        raise exc.NOT_FOUND(
            detail="Student not found."
        )
    
    return await crud.get_grades(
        edbo_id=edbo_id,
        group=student.get("group"),
        subject=body.subject,
        date=date
    )

@router.get("/grades/{edbo_id}/all",
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def get_student_all_grades(edbo_id: int, date: str | None = Query(None)):
    """
        Return all subject grades. 
    """

    student = await UserDB.find_by({"edbo_id": edbo_id})
    if not student:
        raise exc.NOT_FOUND(
            detail="Student not found."
        )

    return await crud.get_grades(
        edbo_id=edbo_id,
        group=student.get("group"),
        date=date
    )

@router.patch("/set-grade/{edbo_id}")
async def set_grade(edbo_id: int, date: str | None = None, body: SetGrade = Body(),
    user: dict = Security(deps.get_current_user, scopes=["teacher"])):
    """
        Set given student grade.
    """
    if body.subject not in user.get("disciplines"):
        raise exc.FORBIDDEN(
            detail="You don't have access to this discipline."
        )
    
    UserDB.COLLECTION_NAME = "students"
    student = await UserDB.find_by({"edbo_id": edbo_id})
    if not student:
        raise exc.NOT_FOUND(
            detail="Student not found."
        )
    
    if not date:
        date = datetime.now().strftime("%d-%m-%Y") 
    
    GradeDB.COLLECTION_NAME = student.get("group")
    await GradeDB.update_one(
        filter={"edbo_id": edbo_id},
        update={
            f"grades.{body.subject}.{date}": body.grade}
    )
    raise exc.OK(
        detail="Student grade successfully added."
    )