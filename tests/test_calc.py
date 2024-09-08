from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_get_users () :
    res = client.get('/')
    print(res.json())