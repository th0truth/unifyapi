from datetime import datetime
from typing import List
from fastapi import (
    APIRouter,
    Security,
    Query,
    Body
)

from api.deps import get_current_user
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

from core import exc
import crud

router = APIRouter(tags=["Students"])

UserDB.COLLECTION_NAME = "students"

@router.post("/create",
    dependencies=[Security(get_current_user, scopes=["admin"])])
async def create_student(student: StudentCreate = Body()):
    """
    Create a student account.
    """
    group = await GroupDB.find_by({"group": student.group})
    if not group:
        raise exc.NOT_FOUND("The student's group not found.")
    return await crud.create_user(user=student)

@router.get("/all/{group}", response_model=List[Student],
    dependencies=[Security(get_current_user, scopes=["teacher", "admin"])])
async def read_students(
        group: str,
        skip: int = 0,
        length: int | None = None
    ) -> List[Student]:
    """
    Return a list of all existing students from the given group.
    """
    return await crud.read_users(role="students", filter="group", value=group, skip=skip, length=length)

@router.post("/grades/my")
async def get_current_student_grades(
        user: dict = Security(get_current_user, scopes=["student"]),
        date: str | None = None,
        body: Grade = Body()
    ):
    """
    Fetch the current user's grades by `subject`.    
    """
    return await crud.get_grades(
        edbo_id=user.get("edbo_id"),
        group=user.get("group"),
        subject=body.subject,
        date=date
    )

@router.get("/grades/my/all")
async def get_current_student_all_grades(
        user: dict = Security(get_current_user, scopes=["student"]),
        date: str | None = None
    ):
    """
    Fetch all grades for the current user.
    """
    return await crud.get_grades(
        edbo_id=user.get("edbo_id"),
        group=user.get("group"),
        date=date
    )

@router.post("/grades/{edbo_id}",
    dependencies=[Security(get_current_user, scopes=["teacher", "admin"])])
async def get_student_grades(
        edbo_id: int,
        date: str | None = Query(None),
        body: Grade = Body() 
    ):
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
    dependencies=[Security(get_current_user, scopes=["teacher", "admin"])])
async def get_student_all_grades(
        edbo_id: int,
        date: str | None = Query(None),
    ):
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
async def set_grade(
        edbo_id: int,
        date: str | None = None,
        body: SetGrade = Body(),
        user: dict = Security(get_current_user, scopes=["teacher"]),
    ):
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