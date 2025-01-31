from typing import List
from fastapi import (
    APIRouter,
    Security,
    Body,
)

from core.schemas.user import UserDB
from core.schemas.student import (
    StudentCreate,
    StudentPublic,
    # StudentSheet
)

from core.services.gsheets import GSheets

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







@router.get("/grades/{edbo_id}/{subject}/")
async def read_student_grades(edbo_id: int, subject: str):
    UserDB.COLLECTION_NAME = "students"
    
    student = await UserDB.find_by({"edbo_id": edbo_id})
    if not student:
        raise exc.NOT_FOUND("Student not found.")
    student_group: str = student.get("group")
    UserDB.COLLECTION_NAME = "teachers"
    class_teacher_edbo: int = student.get("class_teacher") 
    teacher: dict = await UserDB.find_by({"edbo_id": class_teacher_edbo})
    if not teacher:
        raise exc.NOT_FOUND("Teacher not found.")
    groups: dict = teacher.get("groups")
    for group, url in groups.items():
        if group == student_group:                
            break
    
    gs = GSheets(spreadsheet_url=url)
    return gs.worksheet.get("A1:F2")

