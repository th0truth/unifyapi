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
from core import exc
import crud

router = APIRouter(tags=["Teachers"])

UserDB.COLLECTION_NAME = "teachers"

@router.post("/create", dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def create_teacher(user: TeacherCreate = Body()):
    """
        Create a new teacher account.
    """

    return await crud.create_user(user=user)

@router.get("/count", dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def count_teachers():
    """
    
    """
    
    

# @router.post("/count", response_model=Dict[str, int],
#              dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
# async def count_teachers(body: TeacherCount = Body()):
#     """
#         # Count of teachers by 'filter'.
#     """

# #     count = await crud.count_users(collection="teachers", filter={"specialities": body.specialities})
# #     if not count.values():
# #         raise exc.NOT_FOUND(detail="There are no teachers with these specialities.")
# #     return count 