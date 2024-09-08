import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models

client = TestClient(app)
user_id = None
user_informations = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "0123456789",
    "password": "strong_password",
}

@pytest.fixture(scope="module")
def create_user():
    user = {
        "user": user_informations,
    }
    response = client.post("/users/create", json=user)
    assert response.status_code == 201
    user_id = response.json().get("id")
    assert user_id is not None
    yield user_id

def test_create_user_success(create_user):
    assert create_user is not None

def test_delete_user_success(create_user):
    user_id = create_user
    response = client.delete(f"/users/delete/{user_id}")
    assert response.status_code == 204
