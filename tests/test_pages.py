import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import app, verify_token, TokenData, UserCreate, pwd_context, User, UserBase, get_safety_session, \
    UserUpdate
from sqlmodel import create_engine, StaticPool, SQLModel, Session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_safety_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="create_user")
def create_user_fixture():
    user = UserCreate(
        username='Deadpond',
        password='qwe123',
        personal_username='Dive',
        sympathy='Barsik'
    )
    user_hashed_password = pwd_context.hash(user.password)
    user_extra_data = {"hashed_password": user_hashed_password}
    user_mapped = User.model_validate(user, update=user_extra_data)
    return user_mapped


@pytest.fixture(name='token')
def token_fixture():
    def override_verify_token():
        fake_token = TokenData(username='Deadpond')
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
    response.cookies.set('access-token', 'fake_cookie')
    response = client.get('/log_out')
    response.cookies.delete('access-token')
    assert response.status_code == 200
    assert '<!doctype html>' in response.text
    assert response.cookies.get('access-token') is None


def test_get_settings_page(
        client: TestClient,
        session: Session,
        create_user: User,
        token: TokenData
):
    session.add(create_user)
    session.commit()
    response = client.get('/settings')
    assert response.status_code == 200
    assert '<!doctype html>' in response.text


def test_get_settings_update_page(
        token: TokenData,
        session: Session,
        create_user: User,
        client: TestClient
):
    session.add(create_user)
    session.commit()
    response = client.get('/settings_update')
    assert response.status_code == 200
    assert '<!doctype html>' in response.text


def test_update_user(
        session: Session,
        create_user: User,
        client: TestClient
):
    session.add(create_user)
    session.commit()
    response = client.post(
        f"/users/{create_user.id}", data={"sympathy": "Marsik"}
    )
    assert response.status_code == 200
    assert '<!doctype html>' in response.text


def test_update_user_non_existing(
        session: Session,
        create_user: User,
        client: TestClient
):
    session.add(create_user)
    session.commit()
    response = client.post(
        "/users/2", data={"sympathy": "Marsik"}
    )
    assert response.status_code == 404
    assert '<!doctype html>' in response.text
