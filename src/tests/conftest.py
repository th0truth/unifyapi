from motor.motor_asyncio import AsyncIOMotorClient 
from fastapi import FastAPI
from httpx import AsyncClient
import pytest

from app.main import app, MongoDB
from app.core.config import settings

@pytest.fixture(scope="session")
async def db_session():
    client = AsyncIOMotorClient(
        f"mongodb+srv://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}.mongodb.net"
    )
    client.admin.command("ping")
    yield client
    client.close()

# @pytest.fixture(scope="function")
# def test_client(db_session):
#     def override_get_db():
#         try:
#             yield db_session
#         finally:
#             db_session.close()

#     app.dependency_overrides[get_db] = override_get_db
#         yield ac
#     app.dependency_overrides.clear()
