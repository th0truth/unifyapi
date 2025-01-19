from typing import Annotated, List, Dict, Any
from fastapi import APIRouter, Security
from core.schemas.user import UserDB
from core.schemas.student import (
    StudentPublic,
    StudentPrivate
)
import api.deps as deps
import crud

router = APIRouter(tags=["Students"])

UserDB.DATABASE_NAME = "college"
UserDB.COLLECTION_NAME = "ipz12"

@router.get("/all", response_model=List[StudentPublic], dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def read_students(group) -> List[Dict[str, Any]]:
    """Return a list of all existing students."""
    return await crud.read_users()

@router.get("/studentId/{edbo_id}", response_model=StudentPrivate)
async def read_student(edbo_id: Annotated[int, Security(deps.get_current_user, scopes=["teacher", "admin"])]) -> StudentPrivate:
    """Return a student's data by 'edbo_id'."""
    return await crud.read_user(edbo_id=edbo_id)

