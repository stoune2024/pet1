import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session, StaticPool
from app.main import app, get_session, UserCreate, User, pwd_context
from fastapi.encoders import jsonable_encoder


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


def test_create_user(client: TestClient):
    response = client.post(
        "/reg/", data={"username": "Deadpond", "password": "qwerty123"}
    )
    assert response.status_code == 200
    assert '<!doctype html>' in response.text


def test_create_user_incomplete(client: TestClient):
    response = client.post(
        "/reg/", data={"username": "Deadpond"}
    )
    assert response.status_code == 422


def test_create_user_invalid(client: TestClient):
    response = client.post(
        "/reg/", json={"username": "Deadpond", "password": "qwerty123"}
    )
    assert response.status_code == 422


def test_read_users(session: Session, client: TestClient):
    user_1 = UserCreate(username='Deadpond', password='Dive Wilson')
    user_2 = UserCreate(username='Rusty-Man', password='Tommy Sharp', sex='male')

    user_1_hashed_password = pwd_context.hash(user_1.password)
    user_2_hashed_password = pwd_context.hash(user_2.password)

    user_1_extra_data = {"hashed_password": user_1_hashed_password}
    user_2_extra_data = {"hashed_password": user_2_hashed_password}


    user_1_mapped = User.model_validate(user_1, update=user_1_extra_data)
    user_2_mapped = User.model_validate(user_2, update=user_2_extra_data)

    session.add(user_1_mapped)
    session.add(user_2_mapped)
    session.commit()

    response = client.get('/users/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 2
