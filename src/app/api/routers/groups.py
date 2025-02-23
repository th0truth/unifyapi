from typing import (
    Dict,
    List
)
from fastapi import (
    APIRouter,
    Security,
    Body
)

from core.schemas.user import (
    UserDB,
    ROLE,
    DEGREE
)
from core.schemas.teacher import (
    Teacher
)
from core.schemas.group import (
    Group,
    GroupDB
)
from core import exc
import api.deps as deps

router = APIRouter(tags=["Groups"])

@router.get("/read/my", response_model=Group)
async def read_my_group(user: dict = Security(deps.get_current_user, scopes=["student", "teacher"])):
    """
        Retrieves the student group.  
    """
    
    role: ROLE = user.get("role")
    match role:
        case "students":
            GroupDB.COLLECTION_NAME = user.get("degree")            
            group = await GroupDB.find_by({"group": user.get("group")})

            if not group:
                raise exc.NOT_FOUND(
                    detail="The student's group was not found")
            
            teacher_edbo = group.pop("class_teacher_edbo")
            UserDB.COLLECTION_NAME = "teachers"
            group.update({
                "disciplines": [discipline for discipline in group.get("disciplines")],
                "class_teacher": Teacher(**await UserDB.find_by({"edbo_id": teacher_edbo}))})
        case "teachers":
            group = await GroupDB.find_by({"class_teacher_edbo": user.get("edbo_id")})
            if not group:
                raise exc.NOT_FOUND(
                    detail="Your don't have your own group.")
        case _:
            raise exc.INTERNAL_SERVER_ERROR()
    return group

@router.get("/read/all", response_model=Dict[str, List[Group]],
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_groups():
    """
        Return all student groups. 
    """

    group_list = {}
    degrees = await GroupDB.get_collections()
    for degree in degrees:
        GroupDB.COLLECTION_NAME = degree
        group = await GroupDB.find_many()
        group_list.update({degree: group})
    try:     
        return group_list 
    except:
        raise exc.INTERNAL_SERVER_ERROR(
            detail="An error occured while getting groups."
        )

@router.get("/read/{group}", response_model=Group,
            dependencies=[Security(deps.get_current_user, scopes=["teacher", "admin"])])
async def read_group(group: str):
    """
        Return the specified group.
    """

    degrees = await GroupDB.get_collections()
    for degree in degrees:
        GroupDB.COLLECTION_NAME = degree
        _group = await GroupDB.find_by({"group": group})
    if not _group:
        raise exc.NOT_FOUND(detail="Given group not found.")
    return _group

@router.post("/create/{degree}", dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def create_group(degree: DEGREE, body: Group = Body()):
    """
        Create the student group.
    """

    degrees = await GroupDB.get_collections()
    for _degree in degrees:
        GroupDB.COLLECTION_NAME = _degree
        if await GroupDB.find_by({"group": body.group}):
            raise exc.CONFLICT(
                detail="Group already exits.")
    
    GroupDB.COLLECTION_NAME = degree
    await GroupDB.create(doc=body.model_dump(exclude={"additionalProp1"}))
    raise exc.CREATED(
        detail="Group created successfully.")

@router.delete("/delete/{group}", deprecated=True, dependencies=[Security(deps.get_current_user, scopes=["admin"])])
async def delete_group(group: str):

    degrees = await GroupDB.get_collections()
    for degree in degrees:
        GroupDB.COLLECTION_NAME = degree
        _group = await GroupDB.find_by({"group": group})
        if not _group:
            print("dasd")

    await GroupDB.delete_document_by({"group": group})
    raise exc.OK(
        detail="The given group has been deleted.") 