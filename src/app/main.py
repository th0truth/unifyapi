from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI

from .core.config import settings
from .api.api import api_router
from .core.db import MongoDB

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with MongoDB() as client:
        yield client 

app = FastAPI(
    title=settings.NAME,
    description=settings.DESCRIPTION,
    summary=settings.SUMMARY,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(api_router, prefix=settings.API_V1_STR)