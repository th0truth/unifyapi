from fastapi import APIRouter
from .routers import (
    login,
    admin,
    users,
    students
)

api_router = APIRouter()

api_router.include_router(login.router, prefix="/login")
api_router.include_router(users.router, prefix="/users")
api_router.include_router(students.router, prefix="/students")
api_router.include_router(admin.router, prefix="/admin")