from typing import List, Dict, Any
from fastapi import (
    APIRouter,
    Depends,
    Security,
    Body,
    Path,
)

from core.schemas.user import UserDB
from core.schemas.student import (
    StudentCreate,
    StudentPublic,
    StudentPrivate
)
import api.deps as deps
from core import exc
import crud

router = APIRouter(tags=["Students"])

UserDB.COLLECTION_NAME = "students"

@router.post("/create", dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def create_student(user: StudentCreate = Body()):
    """
        Create a student account.
    """

    return await crud.create_user(user=user)

@router.get("/all/{group}", response_model=List[StudentPublic],
        dependencies=[Security(deps.get_current_user, scopes=["lecturer", "admin"])])
async def read_students(group: str, skip: int = 0, length: int | None = None) -> List[StudentPublic]:
    """
        Return a list of all existing students from the given group.\n
        e.g: group=IPZ-12 or KI-11
    """

    return await crud.read_users(role="students", filter="group", value=group, skip=skip, length=length)