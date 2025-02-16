from typing import (
    List,
    Dict,
    Any
)

from core.config import settings
from core.security.utils import Hash
from core.services.gsheets import GSheets
 
from core.schemas.user import (
    UserCreate,
    UserDB,
    ROLE
)
from core.schemas.group import (
    GroupDB
)

from core import exc

async def get_user_by_username(*, username: str) -> dict | None:
    """
        Find user by username. e.g 'edbo_id' or 'email' 
    """
    collections = await UserDB.get_collections()
    for collection in collections:
        UserDB.COLLECTION_NAME = collection
        user = await UserDB.find_by({"email": str(username)})
        if not user:
            try:
                user = await UserDB.find_by({"edbo_id": int(username)})
            except:
                continue
        if user:
            break
    return user

async def get_user_fullname(*, user: dict) -> str:
    """
        Return the full name of the user.
    """
    return "{} {} {}".format(
        user.get("last_name"), user.get("first_name"), user.get("middle_name"))

async def create_user(*, user: UserCreate) -> bool:
    """
        Create a new user in the MongoDB collection.
    """
    if await UserDB.find_by({"edbo_id": user.edbo_id}):
        raise exc.UNPROCESSABLE_CONTENT(detail="User already exits.")
    UserDB.COLLECTION_NAME = user.role
    user.password = Hash.hash(user.password)
    await UserDB.create(user.model_dump())
    raise exc.CREATED(detail="User created successfully.")

async def count_users(*, collection: ROLE, filter: dict):
    """
        Read count of users.
    """
    UserDB.COLLECTION_NAME = collection
    return await UserDB.count_documents(filter)

async def read_users(*, role: ROLE, filter: str | None = None, value: Any, skip: int = 0, length: int | None = None) -> List[Dict[str, Any]]:
    """
        Read all users from the MongoDB collection.
    """
    UserDB.COLLECTION_NAME = role
    return await UserDB.find_many(
        filter=filter, value=value, skip=skip, length=length)

async def read_user(*, edbo_id: int) -> Dict[str, Any]:
    """
        Read user from the MongoDB collection.
    """
    user = await get_user_by_username(username=edbo_id)
    if not user:
        raise exc.NOT_FOUND(detail="User not found.")
    return user 

async def update_all_users(*, collection: ROLE, filter: dict, update: dict):
    """
        Update users data.
    """
    UserDB.COLLECTION_NAME = collection
    await UserDB.update_many(
        filter=filter,
        update=update)
    raise exc.OK(
        detail="User accounts has been updated.")

async def update_user(*, edbo_id: int, data: dict):
    """
        Update user data.
    """
    user = await get_user_by_username(username=edbo_id)
    if not user:
       raise exc.NOT_FOUND(detail="User not found.") 
    await UserDB.update_one(
        filter={"edbo_id": user.get("edbo_id")},
        update=data)
    raise exc.OK(
        detail="The user account has been updated.")

async def delete_user(*, user: dict):
    """
        Delete user from the MongoDB collection by 'edbo_id'.
    """
    
    if not user:
        raise exc.NOT_FOUND(
            detail="User not found.")
    await UserDB.delete_document_by({"edbo_id": user.get("edbo_id")})
    raise exc.OK(
        detail="The user account has been deleted")

async def authenticate_user(*, username: str | int, plain_pwd: str) -> dict:
    """
        Authenticate user credentials.
    """
    user = await get_user_by_username(username=username)
    if not user or not Hash.verify(plain_pwd, user["password"]):
        raise exc.UNAUTHORIZED(
            detail="Couldn't validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    # Check user scopes (privileges)
    scopes = user.get("scopes")
    for scope in scopes:
        if scope not in settings.scopes:
            raise exc.UNAUTHORIZED("Invalid user credentials.")
    return user

async def get_grades(*, student_name: str, group: str, discipline: str) -> dict:
    group: dict = await GroupDB.find_by({"group": group})
    if not group:
        raise exc.NOT_FOUND("The student's group was not found")
    try:
        url = group["disciplines"][discipline]
    except:
        raise exc.INTERNAL_SERVER_ERROR("An error occured while getting discipline.") 

    gs = GSheets(spreadsheet_url=url)

    date = gs.worksheet.row_values(row=6)[1:]
    cell = gs.find_by(query=student_name)

    grades = gs.worksheet.row_values(cell.address)[1:]
    if not grades:
        raise exc.NOT_FOUND(
            detail="The specified subject for student grades was not found.")
    
    counter, avg = 0, 0
    grades_list = {}
    try:
        for j, grade in enumerate(grades):
            if not grade:
                continue
            elif not grade in [" ", "", "Н"]:
                grade = int(grade)
                counter += 1 
                avg += grade
            grades_list.update({date[j]: grade})
        return {
            "grades": grades_list,
            "average": round((avg / counter), 2)
        }
    except Exception as err:
        print(err) 
        raise exc.INTERNAL_SERVER_ERROR(
            detail="Something went wrong. Try again later.")