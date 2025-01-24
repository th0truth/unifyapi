from fastapi import APIRouter
from .routers import (
    auth,
    users,
    students,
    lecturers,
    schedule
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(users.router, prefix="/users")
api_router.include_router(students.router, prefix="/students")
api_router.include_router(lecturers.router, prefix="/lecturers")
api_router.include_router(schedule.router, prefix="/schedule")