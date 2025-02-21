import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, StaticPool, SQLModel, Session
from app.main import app, OAuth2PasswordRequestForm, authenticate_user, UserCreate, pwd_context, User, get_session
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
    app.dependency_overrides[get_session] = get_session_override
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


def test__login_for_access_token(session: Session,client: TestClient, create_user: User):
    session.add(create_user)
    session.commit()
    user_db = session.get(User, create_user.id)

    response = client.post("/token", data={"username": "Deadpond", "password": "qwe123"})
    data = response.json()
    assert response.status_code == 200
    assert data['token_type'] == 'bearer'
