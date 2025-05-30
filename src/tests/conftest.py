from httpx import ASGITransport, AsyncClient
from typing import AsyncGenerator
import pytest_asyncio 

from app.main import app

@pytest_asyncio.fixture(scope="module")
async def test_async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        yield async_client

# @pytest_asyncio.fixture(scope="module")
# async def test_get_current_user()