from typing import List
from fastapi import (
    APIRouter,
    Security,
    Depends,
    Body
)
import uuid

from core.schemas.user import UserDB, ROLE
from core.schemas.schedule import (
    Schedule,
    ScheduleCreate,
    ScheduleTeacher,
    ScheduleDB
)
from core.services.gsheets import GSheets
from core import exc
import api.deps as deps

router = APIRouter(tags=["Schedule"])

ScheduleDB.DATABASE_NAME = "schedule"

async def get_teacher_info(lesson: dict):
    UserDB.COLLECTION_NAME = "teachers"
    edbo_id: int = lesson.pop("teacher_edbo")
    user = await UserDB.find_by({"edbo_id": edbo_id})
    lesson.update({"teacher": ScheduleTeacher(**user).model_dump()})

async def get_grade(lesson: dict, name: str, _student_grades: dict):
    grade = 0
    UserDB.COLLECTION_NAME = "teachers"
    group: str = lesson["group"]
    subject: str = lesson["name"]
    teacher = await UserDB.find_by(
        {f"groups.{group}.{subject}": {"$exists": True}}) #Шукається вчитель, який має предмет subject у групі group.
    if not teacher:
        grade = None                                      #Якщо вчитель не знайдений → оцінки не буде
    else:
        if _student_grades.get(subject) is None:          #Якщо оцінки з таблиці ні разу не діставались, то вони дістануться і добавляться в змінну, аби повторно їх не діставати з таблиці
            groups: dict = teacher.get("groups")                  #Отримується словник groups, у якому містяться предмети та посилання на Google-таблиці.
            for _group, _subject in groups.items():               #Перебираються групи (_group) і предмети (_subject).
                if _group == group:
                    url: str = _subject[subject]                  #Якщо знайдена потрібна група, витягується URL її Google-таблиці.
                    break
            
            gs = GSheets(spreadsheet_url=url)                     #Отримання рядку з датами і оцінками учня
            dates = gs.get_row(gs.ROW_GRADES)[1:]
            student_grades = gs.get_row(gs.find_by(query=name).row)[1:]
            
            student_grades_subject = {}
            for item in range(len(dates)):                         #Додавання оцінок в змінну
                student_grades_subject.update({ f"{dates[item]}" : student_grades[item]})
            _student_grades.update({ f"{subject}" : student_grades_subject})
        
        try:
            time = f"{lesson["time"][-5:-3]}.{lesson["time"][-2:]}.{lesson["time"][0:4]}" #Формат дати з бд в таблицю
            grade = _student_grades[subject][time]
        except:
            grade = 666

    if grade is not None:
        lesson.update({"grade": grade})

@router.get("/my", response_model=List[Schedule])
async def read_my_schedule(user: dict = Depends(deps.get_current_user)):
    """
        Return the schedule for me. 
    """

    role: ROLE = user.get("role")
    match role:
        case "students":
            group: str = user.get("group")
            ScheduleDB.COLLECTION_NAME = group
            schedule = await ScheduleDB.find_many(filter="group", value=group)
            _student_grades = {}
            for lesson in schedule:
                await get_teacher_info(lesson=lesson)
                await get_grade(lesson=lesson,
                                _student_grades=_student_grades, 
                                name=f"{user["last_name"]} {user["first_name"]} {user["middle_name"]}")
        case "teachers":
            collections = await ScheduleDB.get_collections()
            for collection in collections:
                ScheduleDB.COLLECTION_NAME = collection                
                schedule = await ScheduleDB.find_many(
                    filter="teacher_edbo", value=user.get("edbo_id"))
                for lesson in schedule:
                    await get_teacher_info(lesson=lesson)
        case _:
            raise exc.UNPROCESSABLE_CONTENT()
    return schedule                

@router.get("/{group}", response_model=List[Schedule],
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_group_schedule(group: str, skip: int | None = None, length: int | None = None):
    """
        Return the schedule for the given group. 
    """
    
    ScheduleDB.COLLECTION_NAME = group
    schedule = await ScheduleDB.find_many(skip=skip, length=length)
    if not schedule:
        raise exc.NOT_FOUND(detail="Group schedule not found.")
    for lesson in schedule:
        await get_teacher_info(lesson=lesson)
    return schedule

@router.get("/{group}/{id}", response_model=Schedule,
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_schedule_by_id(group: str, id: str):
    """
        Return the schedule for the given group with a unique id. 
    """
    
    ScheduleDB.COLLECTION_NAME = group
    lesson = await ScheduleDB.find_by({"lesson_id": id})
    if not lesson:
        raise exc.NOT_FOUND(detail="Lesson not found.")
    await get_teacher_info(lesson=lesson)
    return lesson

@router.post("/create/lesson")
async def create_lesson(body: ScheduleCreate = Body(), 
    user: dict = Security(deps.get_current_user, scopes=["teacher", "admin"])):                   
    """
        Create a lesson.
    """

    ScheduleDB.COLLECTION_NAME = body.group
    await ScheduleDB.create(
        {"teacher_edbo": user.get("edbo_id"),
        "lesson_id": str(uuid.uuid4()),
         **body.model_dump()})
    raise exc.CREATED(
        detail="The lesson has been created successfully."
    )