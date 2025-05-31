from httpx import AsyncClient
import pytest

from app.core.schemas.etc import Token

from app.core.security.utils import Hash  

from app.core.config import settings

@pytest.mark.asyncio
async def test_auth_login(
    test_async_client: AsyncClient,
    mock_mongo_db
) -> None:
    pwd = "testpassword" 
    credentials = {"edbo_id": "291782927", "password": Hash.hash(pwd)}

    await mock_mongo_db.users.insert_one(credentials)

    print(await mock_mongo_db.users.find_one({"edbo_id": credentials["edbo_id"]}))

    response = await test_async_client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": credentials["edbo_id"], "password": pwd}, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200
    # assert "token" in response.json()