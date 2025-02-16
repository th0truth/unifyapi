from fastapi import APIRouter
from .routers import (
    auth,
    teachers,
    user,
    users,
    groups,
    students,
    schedule,
    lessons
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(user.router, prefix="/user")
api_router.include_router(users.router, prefix="/users")
api_router.include_router(groups.router, prefix="/groups")
api_router.include_router(students.router, prefix="/students")
api_router.include_router(teachers.router, prefix="/teachers")
api_router.include_router(schedule.router, prefix="/schedule")
api_router.include_router(lessons.router, prefix="/lessons")