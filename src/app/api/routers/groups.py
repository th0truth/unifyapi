from typing import Annotated, Dict, List
from fastapi import (
    HTTPException,
    APIRouter,
    status,
    Security,
    Depends,
    Body
)

from core.db import MongoClient

from core.schemas.user import UserBase
from core.schemas.student import StudentBase
from core.schemas.group import (
    GroupBase,
    GroupCreate
)
from api.dependencies import (
    get_mongo_client,
    get_current_user
)

router = APIRouter(tags=["Groups"])

async def get_disciplines(
        mongo: MongoClient,
        *,
        group: dict
    ) -> dict:
    user_db = mongo.get_database("users")
    collection = user_db.get_collection("teachers")
    group.update(
        {"disciplines": [{discipline: UserBase(**await collection.find_one({"edbo_id": edbo_id}))} for discipline, edbo_id in group["disciplines"].items()]}
    )
    return group


@router.post("/create",
    dependencies=[Security(get_current_user, scopes=["admin"])])
async def create_group(
        body: Annotated[GroupCreate, Body],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Create the student group.
    """
    group_db = mongo.get_database("groups")
    collections = await group_db.list_collection_names()
    if body.degree not in collections:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group degree not found."
        )
    for _name in collections: 
        collection = group_db.get_collection(_name)
        if await collection.find_one({"group": body.group}):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Group already exits."
            )
    collection = group_db.get_collection(body.degree)
    await collection.insert_one(body.model_dump())
    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="Group created successfully."
    )

@router.get("/read/my", response_model=GroupBase)
async def get_current_user_group(
        user: Annotated[dict, Security(get_current_user, scopes=["student", "teacher"])],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Return the student group.  
    """
    group_db = mongo.get_database("groups")
    role = user.get("role")
    match role:
        case "students":
            student = StudentBase(**user)
            collection = group_db.get_collection(student.degree)
            group: dict = await collection.find_one({"group": student.group})
            if not group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="The student's group not found"
                )
        case "teachers":
            for name in await group_db.list_collection_names():
                collection = group_db.get_collection(name)
                group: dict = await collection.find_one({"class_teacher_edbo": user.get("edbo_id")})
                if group: break 
            if not group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Group not found"
                )
    group = await get_disciplines(mongo, group=group)
    return group

@router.post("/read", response_model=GroupBase,
    dependencies=[Security(get_current_user, scopes=["teacher", "admin"])])
async def get_group(
        name: Annotated[str, Body],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Read an group by `name`.
    """
    group_db = mongo.get_database("groups")
    for _name in await group_db.list_collection_names():
        collection = group_db.get_collection(_name)
        group = await collection.find_one({"group": name})
        if group: break
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found."
        )
    group = await get_disciplines(mongo, group=group)
    return group

@router.get("/read/all", response_model=Dict[str, List[GroupBase]],
    dependencies=[Security(get_current_user, scopes=["teacher", "admin"])])
async def read_groups(
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Return all student groups. 
    """
    groups = {}
    group_db = mongo.get_database("groups")
    for _name in await group_db.list_collection_names():
        collection = group_db.get_collection(_name)
        group_list = await collection.find().to_list()
        groups.update({_name: group_list})
    return groups
 
@router.delete("/delete",
    dependencies=[Security(get_current_user, scopes=["admin"])])
async def delete_group(
        name: Annotated[str, Body],
        mongo: Annotated[MongoClient, Depends(get_mongo_client)]
    ):
    """
    Delete the student group.
    """
    group_db = mongo.get_database("groups") 
    for _name in await group_db.list_collection_names():
        collection = group_db.get_collection(_name)
        group = await collection.find_one({"group": name})
        if group: break
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given group not found."
        )
    await collection.delete_one(group)
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="The group has been deleted."
    )