from fastapi.testclient import TestClient
from app.main import app, verify_token, TokenData

client = TestClient(app)

def override_verify_token():
    fake_token = TokenData(username='fake_username')
    return fake_token

app.dependency_overrides[verify_token] = override_verify_token


def test_get_index():
    response = client.get("/")
    assert response.status_code == 200
    assert '<!doctype html>' in response.text

def test_get_barsik_page():
    response = client.get("/barsik")
    assert response.status_code == 200
    assert '<!doctype html>' in response.text

def test_get_marsik_page():
    response = client.get("/marsik")
    assert response.status_code == 200
    assert '<!doctype html>' in response.text

def test_bonus_page():
    response = client.get("/bonus")
    assert response.status_code == 200
    assert '<!doctype html>' in response.text