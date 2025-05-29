from fastapi import FastAPI
from httpx import AsyncClient
import pytest

from app.main import app
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
