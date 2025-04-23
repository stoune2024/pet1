import pytest
from fastapi.testclient import TestClient
from app.main import app, verify_token, TokenData


@pytest.fixture(name='client')
def client_fixture():
    client = TestClient(app)
    return client


@pytest.fixture(name='token')
def token_fixture():
    def override_verify_token():
        fake_token = TokenData(username='fake_username')
        return fake_token

    app.dependency_overrides[verify_token] = override_verify_token
    yield override_verify_token()
    app.dependency_overrides.clear()


def test_get_index(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert '<!doctype html>' in response.text


def test_get_barsik_page(client: TestClient):
    response = client.get("/barsik")
    assert response.status_code == 200
    assert '<!doctype html>' in response.text


def test_get_marsik_page(client: TestClient):
    response = client.get("/marsik")
    assert response.status_code == 200
    assert '<!doctype html>' in response.text


def test_get_bonus_page(client: TestClient, token: TokenData):
    response = client.get("/bonus")
    assert response.status_code == 200
    assert '<!doctype html>' in response.text


def test_get_oauth_page(client: TestClient):
    response = client.get("/oauth")
    assert response.status_code == 200
    assert '<!doctype html>' in response.text


def test_get_reg_page(client: TestClient):
    response = client.get("/reg")
    assert response.status_code == 200
    assert '<!doctype html>' in response.text


def test_get_suc_oauth_page(client: TestClient, token: TokenData):
    response = client.get("/suc_oauth")
    assert response.status_code == 200
    assert '<!doctype html>' in response.text


def test_log_out_page(client: TestClient):
    response = client.get('/log_out')
    assert response.status_code == 200
    assert '<!doctype html>' in response.text
    assert response.cookies['access-token'] != True
