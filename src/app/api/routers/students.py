from typing import List, Dict, Any
from fastapi import APIRouter, Path, Security
from core.schemas.user import UserDB
from core.schemas.student import (
    StudentPublic,
    StudentPrivate
)
from core import exc
import api.deps as deps
import crud

router = APIRouter(tags=["Students"])

UserDB.DATABASE_NAME = "users"
UserDB.COLLECTION_NAME = "students"

@router.get("/all/{class_name}",
            response_model=List[StudentPublic], dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_students(class_name: str = Path(min_length=3)) -> List[Dict[str, Any]]:
    """
        Return a list of all existing students from the given class.
    """
    
    return await crud.read_users(collection=class_name)

@router.get("/class/{class_name}/studentId/{username}",
            response_model=StudentPrivate, dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_student(class_name: str = Path(min_length=3), username: str = Path()) -> StudentPrivate:
    """
        Return a student's data by 'edbo_id'.
    """

    classes = await UserDB.get_collections()
    if class_name not in classes:
        raise exc.NOT_FOUND(
            detail="Student not found"
        )
    UserDB.COLLECTION_NAME = class_name
    return await crud.read_user(username=username)

