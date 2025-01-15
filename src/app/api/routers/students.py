from typing import (
    Annotated,
    List,
    Dict,
    Any
)
from fastapi import APIRouter, Path, Depends
from core.schemas.student import (
    StudentPublic,
    StudentPrivate,
)

import crud
import api.deps as deps
router = APIRouter(tags=["Students"])

@router.get("/read-students", response_model=List[StudentPublic])
async def read_students(skip: int = 0, length: int | None = None) -> List[Dict[str, Any]]:
    return await crud.read_users(skip=skip, length=length)

@router.get("/read-student/{edbo_id}", response_model=StudentPrivate)
async def read_student(edbo_id: Annotated[int, Path()]):
    return await crud.read_user(edbo_id=edbo_id)

@router.get("/me", response_model=StudentPrivate)
async def get_current_student(user: Annotated[StudentPrivate, Depends(deps.get_current_user)]) -> StudentPrivate:
    return user