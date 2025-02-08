from typing import Dict
from fastapi import APIRouter, Security, Body

from datetime import datetime

from core.schemas.user import UserDB
from core.schemas.teacher import (
    TeacherCreate,
    TeacherCount
)
from core.schemas.utils import SetGrade

from core.services.gsheets import GSheets

import api.deps as deps
from core import exc
import crud

router = APIRouter(tags=["Teachers"])

UserDB.COLLECTION_NAME = "Teachers"

@router.post("/create", dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def create_teacher(user: TeacherCreate = Body()):
    """
        Create a new teacher account.
    """

    return await crud.create_user(user=user)

@router.post("/all/count", response_model=Dict[str, int],
             dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def count_teachers(body: TeacherCount = Body()):
    """
        Count of teachers by 'filter'.
    """

    count = await crud.count_users(collection="teachers", filter={"specialities": body.specialities})
    if not count.values():
        raise exc.NOT_FOUND(detail="There are no teachers with these specialities.")
    return count 

@router.patch("/set/grade")
async def set_grade(
    user: dict = Security(deps.get_current_user, scopes=["teacher", "admin"]),
    body: SetGrade = Body()):
    """
        Submits a student's grade for a group.
    """
    
    UserDB.COLLECTION_NAME = "students"
    
    student = await UserDB.find_by({"edbo_id": body.edbo_id})
    if not student:
        raise exc.NOT_FOUND("Student not found")
    group_name = student.get("group")
    
    UserDB.COLLECTION_NAME = "groups"
    group = await UserDB.find_by({"group": group_name})
    if body.subject not in user.get("disciplines"):    
        raise exc.INTERNAL_SERVER_ERROR("An error occured while getting discipline.") 
    
    url = group["disciplines"][body.subject]
    
    dt = body.date
    if dt in [None, "", "", "string"]:
        dt = datetime.now().strftime("%m.%d.%Y")
    gs = GSheets(spreadsheet_url=url)    
    date = gs.worksheet.row_values(row=6)[1:]
    index = date.index(dt)

    student_name = "{} {} {}".format(
            student.get("last_name"), student.get("first_name"), student.get("middle_name"))
    
    cell = gs.find_by(query=student_name)
    try:
        gs.worksheet.update_cell(cell.row, index + 2, value=body.grade)
    except:
        raise exc.METHOD_NOT_ALLOWED(
            detail="An error occured while submitting the grade.")
    finally:
        raise exc.OK(
            detail="The grade was submitted successfully")