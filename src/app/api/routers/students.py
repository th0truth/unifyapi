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

@router.get("/read-students", response_model=List[StudentPublic])
async def read_students(skip: int = 0, length: int | None = None) -> List[Dict[str, Any]]:
    """
        Read all existing students.
    """
    return await crud.read_users(skip=skip, length=length)

@router.get("/read-student/{edbo_id}", response_model=StudentPrivate)
async def read_student(edbo_id: Annotated[int, Security(deps.get_current_user, scopes=["teacher", "admin"])]):
    """
        Read a student's data by 'edbo_id'.
    """
    return await crud.read_user(edbo_id=edbo_id)

