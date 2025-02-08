from fastapi import (
    APIRouter,
    Security,
    Body,
)

from core.schemas.user import ROLE
from core.schemas.group import (
    Group,
    GroupDB
)

from core import exc
import api.deps as deps

router = APIRouter(tags=["Groups"])

@router.get("/read/my", response_model=Group)
async def read_my_group(user: dict = Security(deps.get_current_user, scopes=["student", "teacher"])):
    role: ROLE = user.get("role")
    match role:
        case "students":
            group = await GroupDB.find_by({"group": user.get("group")})
            if not group:
                raise exc.NOT_FOUND(
                    detail="The student's group was not found")
        case "teachers":
            group = await GroupDB.find_by({"class_teacher_edbo": user.get("edbo_id")})
            if not group:
                raise exc.NOT_FOUND(
                    detail="Your don't have your own group.")
    return group

@router.get("/read/all", response_model=list[Group],
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_groups():
    groups = await GroupDB.find_many()
    return groups

@router.post("/create", dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def create_group(group: Group = Body()):
    if await GroupDB.find_by({"group": group.group}):
        raise exc.CONFLICT(
            detail="Group already exits.")
    await GroupDB.create(doc=group.model_dump())
    raise exc.CREATED(
        detail="Group created successfully.")

@router.delete("/delete/{group}", dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def delete_group(group: str):
    if not await GroupDB.find_by({"group": group}):
        raise exc.NOT_FOUND(
            detail="Group not found")
    await GroupDB.delete_document_by({"group": group})
    raise exc.OK(
        detail="The given group has been deleted.")