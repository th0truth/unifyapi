from typing import List, Dict, Any
from fastapi import (
    APIRouter,
    Security,
    Body,
)

from core.schemas.user import UserDB
from core.schemas.student import (
    StudentCreate,
    StudentPublic,
    StudentPrivate,
    StudentSubject
)

from core.services.gsheets import GSheets

import api.deps as deps
from core import exc
import crud

router = APIRouter(tags=["Students"])

UserDB.COLLECTION_NAME = "students"

async def _get_student_grades(student_name: str, group: str, subject: str) -> dict:
    UserDB.COLLECTION_NAME = "teachers"
    teacher = await UserDB.find_by(
        {f"groups.{group}.{subject}": {"$exists": True}})
    if not teacher:
        raise exc.NOT_FOUND("Teacher not found.") 
    groups: dict = teacher.get("groups")
    for _group, _subject in groups.items():
        if _group == group:
            url: str = _subject[subject]
            break

    gs = GSheets(spreadsheet_url=url)
    date = gs.worksheet.row_values(row=4)[1:]
    cell = gs.find_by(query=student_name)
    grades = gs.worksheet.row_values(cell.address)[1:]
    if not grades:
        raise exc.NOT_FOUND(
            detail="The specified subject for student grades was not found.")
    grade_list = {}
    try:
        for e, grade in enumerate(grades):
            if not grade:
                continue
            elif not grade in [" ", "", "Н"]:
                grade = int(grade)
            grade_list.update({date[e]: grade})
        return grade_list 
    except:
        raise exc.INTERNAL_SERVER_ERROR(
            detail="Something went wrong. Try again later.")

@router.post("/create", dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def create_student(student: StudentCreate = Body()):
    """
        Create a student account.
    """

    return await crud.create_user(user=student)

@router.get("/all/{group}", response_model=List[StudentPublic],
        dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_students(group: str, skip: int = 0, length: int | None = None) -> List[StudentPublic]:
    """
        Return a list of all existing students from the given group.\n
        e.g: group=IPZ-12 or KI-11
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

@router.post("/my-grades")
async def get_my_grades(user: dict = Security(deps.get_current_user, scopes=["student"]), subject: StudentSubject = Body()):
    """
        Return the student subject's grades.
    """

    student = StudentPrivate(**user)
    grades = await _get_student_grades(
        student_name=f"{student.last_name} {student.first_name} {student.middle_name}",
        group=student.group,
        subject=subject.subject 
    )
    return grades

@router.post("/grades", response_model=Dict[str, Any],
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def get_student_grades(edbo_id: int = Body(), subject: str = Body()):
    """
        Return the specified student's subject grades. 
    """

    UserDB.COLLECTION_NAME = "students"
    student = await UserDB.find_by({"edbo_id": edbo_id})
    if not student:
        raise exc.NOT_FOUND("Student not found.")
    student = StudentPrivate(**student)

    grades = await _get_student_grades(
        student_name=f"{student.last_name} {student.first_name} {student.middle_name}",
        group=student.group,
        subject=subject
    )
    return grades