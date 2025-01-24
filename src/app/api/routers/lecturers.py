from fastapi import APIRouter, Security, Body

from core.schemas.lecturer import (
    LecturerCreate
)
from core.schemas.user import UserDB
import api.deps as deps
import crud

router = APIRouter(tags=["Lecturers"])

UserDB.COLLECTION_NAME = "lecturers"

@router.post("/create", dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def create_lecturer(user: LecturerCreate = Body()):
    """
        Create a new lecturer account.
    """
    return await crud.create_user(user=user)