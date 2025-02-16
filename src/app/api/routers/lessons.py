from fastapi import (
    APIRouter,
    Security,
    Body,
    Query
)
from datetime import datetime
import uuid

from core.schemas.user import UserDB
from core.schemas.schedule import (
    Lesson,
    LessonCreate,
    ScheduleDB
)
from core.schemas.etc import SetGrade
from core.services.gsheets import GSheets

from core import exc
import api.deps as deps
import crud

router = APIRouter(tags=["Lessons"])

@router.post("/create")
async def create_lesson(body: LessonCreate = Body(), 
    user: dict = Security(deps.get_current_user, scopes=["teacher", "admin"])):                   
    """
        Create a lesson.
    """

    groups = await ScheduleDB.get_collections()    
    if body.group not in groups:
        raise exc.NOT_FOUND(
            detail="The group not found.")

    ScheduleDB.COLLECTION_NAME = body.group
    await ScheduleDB.create(
        {"teacher_edbo": user.get("edbo_id"),
        "lesson_id": str(uuid.uuid4()),
         **body.model_dump()})
    raise exc.CREATED(
        detail="The lesson has been created successfully."
    )

@router.post("/my/grades")
async def get_my_grades(
    user: dict = Security(deps.get_current_user, scopes=["student"]), body: Lesson = Body()):
    """
        Return the student subject's grades.
    """

    grades = await crud.get_grades(
        student_name=await crud.get_user_fullname(user=user),
        group=user.get("group"),
        discipline=body.lesson
    )
    return grades

@router.patch("/set/grade")
async def set_grade(
    user: dict = Security(deps.get_current_user, scopes=["teacher", "admin"]), 
    date: str = Query(None), body: SetGrade = Body()):
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
    if body.lesson not in user.get("disciplines"):    
        raise exc.NOT_FOUND("The student discipline not found.") 
    
    url = group["disciplines"][body.lesson]
    
    if date in [None, "", " "]:
        date = datetime.now().strftime("%m.%d.%Y")
    
    gs = GSheets(spreadsheet_url=url)
    dt_cell = gs.worksheet.row_values(row=6)[1:]
    try:
        index = dt_cell.index(date)
    except ValueError:
        raise exc.NOT_FOUND(
            detail=f"Date '{date}' not found in the Google Spreadsheet")

    student_name = await crud.get_user_fullname(user=student)
    cell = gs.find_by(query=student_name)
    try:
        gs.worksheet.update_cell(cell.row, index + 2, value=body.grade)
    except:
        raise exc.METHOD_NOT_ALLOWED(
            detail="An error occured while submitting the grade.")
    finally:
        raise exc.OK(
            detail="The grade was submitted successfully")