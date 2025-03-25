from fastapi import (
    APIRouter,
    Security,
    Body
)

from core.schemas.user import UserDB
from core.schemas.teacher import (
    TeacherCreate,
)
import api.deps as deps
import crud

router = APIRouter(tags=["Teachers"])

UserDB.COLLECTION_NAME = "teachers"

@router.post("/create",
    dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def create_teacher(user: TeacherCreate = Body()):
    """
    Create a new teacher account.
    """
    return await crud.create_user(user=user)