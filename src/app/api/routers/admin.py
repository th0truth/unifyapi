from fastapi import APIRouter, HTTPException, Depends, Header
from typing import (
        Annotated,
        List
    )

from core.schemas.admin import AdminDB
import api.deps as deps

router = APIRouter(tags=["Admin"])

# @router.post("/items/", dependencies=[Depends(deps.get_current_user)])
# async def read_items():
#     return [{"item": "Foo"}, {"item": "Bar"}]