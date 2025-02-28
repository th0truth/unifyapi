from httpx import AsyncClient, ASGITransport
import pytest

from app.main import app

@pytest.mark.anyio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        response = await test_client.get("/")
    assert response.status_code == 404