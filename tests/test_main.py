from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_healthcheck():
    response = client.get("/ok")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
