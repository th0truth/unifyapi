from typing import Dict
from fastapi import APIRouter, Security, Body

from core.schemas.teacher import (
    TeacherCreate,
    TeacherCount,
    GradesGroup
)
from core.schemas.user import UserDB
import api.deps as deps
from core import exc
import crud

from core.services.gsheets import GSheets

router = APIRouter(tags=["Teachers"])

UserDB.COLLECTION_NAME = "Teachers"

async def _get_group_grades(group: str, subject: str) -> Dict[str, dict]:
    UserDB.COLLECTION_NAME = "teachers"
    teacher = await UserDB.find_by(
        {f"groups.{group}.{subject}": {"$exists": True}}) #Шукається вчитель, який має предмет subject у групі group.
    if not teacher:
        raise exc.NOT_FOUND("Teacher not found.")         #Якщо вчитель не знайдений → викликається помилка NOT_FOUND.
    groups: dict = teacher.get("groups")                  #Отримується словник groups, у якому містяться предмети та посилання на Google-таблиці.
    for _group, _subject in groups.items():               #Перебираються групи (_group) і предмети (_subject).
        if _group == group:
            url: str = _subject[subject]                  #Якщо знайдена потрібна група, витягується URL її Google-таблиці.
            break

    gs = GSheets(spreadsheet_url=url)
    data = gs.get_all()
    print(data, 1)
    for _ in range(3):
        data.pop(0)
    print(data, 2)
    # Перетворення у словник
    dates = data[0][1:]  # Дати
    students = [row[0] for row in data[1:]]  # Імена учнів
    grades = [row[1:] for row in data[1:]]  # Оцінки

    print(dates, students, grades)

    result = {}

    for i, date in enumerate(dates):
        day_grades = {}
        for j, student in enumerate(students):
            grade = grades[j][i]
            if grade:  # Якщо оцінка є
                day_grades[student] = grade
            else:  # Якщо оцінки немає, то "Н"
                pass
        result[date] = day_grades

    return result


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
    print(body)
    count = await crud.count_users(collection="teachers", filter={"specialities": body.specialities})
    if not count.values():
        raise exc.NOT_FOUND(detail="There are no teachers with these specialities.")
    return count 

@router.post("/grades/{group}/{subject}", response_model=Dict[str, dict],
             dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def count_teachers(body: GradesGroup = Body()):
    """
        NONE.
    """
    return (await _get_group_grades(group=body.group, subject=body.subject))