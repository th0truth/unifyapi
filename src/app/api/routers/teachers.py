from fastapi import (
    APIRouter,
    Security,
    Body
)

from api.deps import get_current_user

from core.schemas.user import UserDB
from core.schemas.teacher import (
    TeacherCreate,
)
import crud

router = APIRouter(tags=["Teachers"])

UserDB.COLLECTION_NAME = "teachers"

@router.post("/create",
    dependencies=[Security(get_current_user, scopes=["admin"])])
async def create_teacher(user: TeacherCreate = Body()):
    return await crud.create_user(user=user)