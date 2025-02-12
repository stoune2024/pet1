from fastapi.testclient import TestClient

from app.routers.pages import router

client = TestClient(router)


def test_get_index():
    response = client.get("/")
    assert response.status_code == 200
    assert '<!doctype html>' in response.text