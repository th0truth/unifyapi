from fastapi import APIRouter
from .routers import (
    login,
    users,
    students
)

api_router = APIRouter()

api_router.include_router(login.router, prefix="/auth")
api_router.include_router(users.router, prefix="/users")
api_router.include_router(students.router, prefix="/students")