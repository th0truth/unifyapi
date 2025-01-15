from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app=app)

def test_read_users():
    response = client.get("/users/read-users")
    assert response.status_code == 200
    # assert response.json()