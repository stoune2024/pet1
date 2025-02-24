import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, StaticPool, SQLModel, Session
from app.main import app, OAuth2PasswordRequestForm, authenticate_user, UserCreate, pwd_context, User, \
    get_safety_session, verify_token, TokenData
from typing import Annotated
from fastapi import Form

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
        username='fake_user',
        password='fake_password',
        personal_username='Henry',
        sympathy='Marsik'
    )
    user_hashed_password = pwd_context.hash(user.password)
    user_extra_data = {"hashed_password": user_hashed_password}
    user_mapped = User.model_validate(user, update=user_extra_data)
    return user_mapped

@pytest.fixture(name='token')
def token_fixture():
    def override_verify_token():
        fake_token = TokenData(username='fake_username')
        return fake_token
    app.dependency_overrides[verify_token] = override_verify_token
    yield override_verify_token()
    app.dependency_overrides.clear()


def test_login_for_access_token(session: Session, client: TestClient, create_user: User):
    session.add(create_user)
    session.commit()
    response = client.post("/token", data={"username": "fake_user", "password": "fake_password"})
    data = response.json()
    assert response.status_code == 200
    assert data['token_type'] == 'bearer'
    assert data['access_token']


def test_login_for_access_token_user_not_found(session: Session, client: TestClient, create_user: User):
    session.add(create_user)
    session.commit()
    response = client.post("/token", data={"username": "unknown_user", "password": "unknown_password"})
    assert response.status_code == 404
    assert response.headers['WWW-Authenticate'] == "Bearer"
    assert '<!doctype html>' in response.text


def test_validate_login_form(session: Session, client: TestClient, create_user: User, token: TokenData):
    session.add(create_user)
    session.commit()
    response = client.post('/login', data={"username": "fake_user", "password": "fake_password"})
    assert response.status_code == 200
    assert '<!doctype html>' in response.text

def test_validate_login_form_user_not_found(session: Session, client: TestClient, create_user: User, token: TokenData):
    session.add(create_user)
    session.commit()
    response = client.post('/login', data={"username": "unknown_user", "password": "unknown_password"})
    assert response.status_code == 404
    assert '<!doctype html>' in response.text
    assert response.headers['WWW-Authenticate'] == "Bearer"
