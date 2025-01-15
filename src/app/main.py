from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

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

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":    
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=10000,
        reload=True
    )