import pytest
from httpx import ASGITransport, AsyncClient

from app.api.routers import students
from app import main

@pytest.mark.anyio
async def test_read_students():
    async with AsyncClient(
        transport=ASGITransport(app=students.read_students), base_url="http://127.0.0.0:8000"
    ) as ac:
        response = await ac.get("/api/v1/students/read-students")
    assert response.status_code == 200
    # assert