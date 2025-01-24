from typing import List, Dict, Any
from fastapi import (
    APIRouter,
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

@router.post("/create", dependencies=[Security(deps.get_current_user, scopes=["admins"])])
async def create_student(user: StudentCreate = Body()):
    """
        Create a student account.
    """
    return await crud.create_user(user=user)

@router.get("/all/{class_name}", deprecated=True,
            response_model=List[StudentPublic], dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_students(class_name: str = Path(min_length=3)) -> List[Dict[str, Any]]:
    """
        Return a list of all existing students from the given class.
    """
    
    return await crud.read_users(collection=class_name)

@router.get("/class/{class_name}/studentId/{username}", deprecated=True,
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

