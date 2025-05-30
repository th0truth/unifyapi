from httpx import AsyncClient
import pytest

from app.core.schemas.etc import Token

from app.core.config import settings

@pytest.mark.asyncio
async def test_auth_login(
    test_async_client: AsyncClient
) -> None:
    response = await test_async_client.post(
        f"{settings.API_V1_STR}/auth/login", data={"username": "11680600", "password": "82957294a"})
    assert response.status_code == 200
    assert "access_token" in response.json()  