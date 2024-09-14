from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from app.main import app  # Assurez-vous que `app` est l'instance FastAPI
from app.database import Base, get_db  # Importez votre base de données et la fonction `get_db`
from app.models import User, Admin_Parameter
import utils  # Votre module utilitaire

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base=declarative_base()

# Définir une dépendance pour remplacer la base de données dans les tests
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def create_admin_param(db_session):
    param = Admin_Parameter(
        verification_code="123456",
        code_expiry=datetime.utcnow() + timedelta(minutes=10)
    )
    db_session.add(param)
    db_session.commit()
    return param

def test_create_user(create_admin_param):
    print ('testing function')
    response = client.post(
        "/users/create",
        json={
            "user": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone_number": "1234567890",
                "password": "securepassword123"
            },
            "code": "123456"
        }
    )
    assert response.status_code == 201
    assert response.json() == {}

# def test_create_user_invalid_code(create_admin_param):
#     response = client.post(
#         "/users/create",
#         json={
#             "user": {
#                 "first_name": "Jane",
#                 "last_name": "Doe",
#                 "email": "jane.doe@example.com",
#                 "phone_number": "0987654321",
#                 "password": "anotherpassword123"
#             },
#             "code": "654321"
#         }
#     )
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Invalid or expired verification code"
