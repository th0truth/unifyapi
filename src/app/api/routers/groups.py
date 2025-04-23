from fastapi import (
    APIRouter,
    Security,
    Body
)
from api.deps import get_current_user
from core.schemas.user import (
    UserDB,
    ROLE
)
from core.schemas.teacher import Teacher
from core.schemas.group import (
    Group,
    GroupDB
)
from core import exc

router = APIRouter(tags=["Groups"])

@router.get("/read/my", response_model=Group)
async def read_my_group(
        user: dict = Security(get_current_user, scopes=["student", "teacher"])
    ):
    """
    Return the student group.  
    """
    role: ROLE = user.get("role")
    match role:
        case "students":
            GroupDB.COLLECTION_NAME = user.get("degree")
            group = await GroupDB.find_by({"group": user.get("group")})
            if not group:
                raise exc.NOT_FOUND(
                    detail="The student's group not found")
            
            teacher_edbo = group.pop("class_teacher_edbo")
            UserDB.COLLECTION_NAME = "teachers"
            group.update({
                "class_teacher": Teacher(**await UserDB.find_by({"edbo_id": teacher_edbo}))})
        case "teachers":
            collections = await GroupDB.get_collections()
            for collection in collections:
                GroupDB.COLLECTION_NAME = collection
                group = await GroupDB.find_by({"class_teacher_edbo": user.get("edbo_id")})
                if group: break 
            if not group:
                raise exc.NOT_FOUND(
                    detail="You don't have your own group.")
    return group

@router.get("/read/all", response_model=dict[str, list[Group]],
    dependencies=[Security(get_current_user, scopes=["teacher", "admin"])])
async def read_groups():
    """
    Return all student groups. 
    """
    groups = {}
    degrees = await GroupDB.get_collections()
    for degree in degrees:
        GroupDB.COLLECTION_NAME = degree
        group = await GroupDB.find_many()
        groups.update({degree: group})
    return groups

@router.post("/create",
    dependencies=[Security(get_current_user, scopes=["admin"])])
async def create_group(body: Group = Body()):
    """
    Create the student group.
    """
    degrees = await GroupDB.get_collections()
    for degree in degrees:
        GroupDB.COLLECTION_NAME = degree
        if await GroupDB.find_by({"group": body.group}):
            raise exc.CONFLICT(
                detail="Group already exits.")
     
    GroupDB.COLLECTION_NAME = body.degree
    await GroupDB.create(doc=body.model_dump(exclude={"additionalProp1"}))
    raise exc.CREATED(
        detail="Group created successfully.")
 
@router.delete("/delete/{group}",
    dependencies=[Security(get_current_user, scopes=["admin"])])
async def delete_group(group: str):
    degrees = await GroupDB.get_collections()
    for degree in degrees:
        GroupDB.COLLECTION_NAME = degree
        group: dict = await GroupDB.find_by({"group": group})
        if not group:
            raise exc.NOT_FOUND(
                detail="Given group not found."
            )
 
    await GroupDB.delete_document_by({"group": group})
    raise exc.OK(
        detail="The given group has been deleted.") 