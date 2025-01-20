from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.config import settings
from core.db.database import MongoDB
from api.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    with MongoDB() as db:
        yield db

app = FastAPI(
    title=settings.NAME,
    description=settings.DESCRIPTION,
    summary=settings.SUMMARY,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app="main:app",
        host="localhost",
        port=8000,
        reload=True
    )