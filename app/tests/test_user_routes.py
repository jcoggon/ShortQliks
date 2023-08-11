
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_users():
    response = client.get("/v1/users/")
    assert response.status_code == 200
    assert response.json() == [{"username": "user1"}, {"username": "user2"}]

def test_read_user():
    response = client.get("/v1/users/1")
    assert response.status_code == 200
    assert response.json() == {"username": "user1"}
