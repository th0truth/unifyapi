from typing import Annotated, List, Dict, Any
from fastapi import APIRouter, Path, Security
from core.schemas.user import UserDB
from core.schemas.student import (
    StudentCreate,
    StudentPublic,
    StudentPrivate
)
from core import exceptions
import api.deps as deps
import crud

router = APIRouter(tags=["Students"])

UserDB.DATABASE_NAME = "students"
# @router.post("/create")
# async def create_student(student: StudentCreate):
    # return await crud.create_user()

@router.get("/all/{class_name}",
            response_model=List[StudentPublic])#dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_students(class_name: str = Path(min_length=3)) -> List[Dict[str, Any]]:
    """
        Return a list of all existing students from the given class.
    """
    
    return await crud.read_users(collection=class_name)

@router.get("/class/{class_name}/studentId/{edbo_id}",
            response_model=StudentPrivate, dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_student(class_name: str = Path(min_length=3), edbo_id: int = Path()) -> StudentPrivate:
    """
        Return a student's data by 'edbo_id'.
    """

    classes = await UserDB.get_collections()
    if class_name not in classes:
        raise exceptions.NOT_FOUND(
            detail="Student not found"
        )
    UserDB.COLLECTION_NAME = class_name
    return await crud.read_user(edbo_id=edbo_id)

