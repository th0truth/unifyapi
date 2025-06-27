from httpx import ASGITransport, AsyncClient
from typing import AsyncGenerator
import pytest_asyncio 

from mongomock_motor import AsyncMongoMockClient
from asgi_lifespan import LifespanManager
from unittest.mock import AsyncMock

from app.api.dependencies import (
    get_mongo_client
)
from app.crud import authenticate_user
from app.core.db import MongoClient
from app.main import app

# @pytest_asyncio.fixture(autouse=True)
# async def mock_mongo_db():
#     client = AsyncMongoMockClient()    
#     test_db = client.test_db
#     yield test_db
#     await client.drop_database(test_db)
#     client.close() 

# @pytest_asyncio.fixture
# async def test_app(mock_mongo_db, monkeypatch):
#     monkeypatch.setattr(MongoClient, "connect", AsyncMock(return_value=mock_mongo_db))
#     monkeypatch.setattr(MongoClient, "close", AsyncMock())
#     monkeypatch.setattr(MongoClient, "_client", mock_mongo_db.client)
    
#     async def mock_authenticate_user(db, username: str, plain_pwd: str, exclude: list):
#         return {
#             "email": username,
#             "edbo_id": "12345",
#             "role": "user",
#             "scopes": ["students"]
#         }
    
#     app.dependency_overrides[get_mongo_client] = lambda: mock_mongo_db.client
#     app.dependency_overrides[authenticate_user] = mock_authenticate_user
#     async with LifespanManager(app):
#         yield app
#     app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def test_async_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        yield async_client