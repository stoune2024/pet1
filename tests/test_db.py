import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session, StaticPool
from app.main import app, get_db_session, UserCreate, User, pwd_context, UserUpdate
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
    app.dependency_overrides[get_db_session] = get_session_override
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


def test_read_users(session: Session, client: TestClient, create_user: User):
    session.add(create_user)
    session.commit()
    response = client.get('/users/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["personal_username"] == "Dive"


def test_update_user(session: Session, client: TestClient, create_user: User):
    session.add(create_user)
    session.commit()
    user_db = session.get(User, create_user.id)
    response = client.patch(f"/users/{user_db.id}", data={"personal_username": "Dave"})
    data = response.json()
    assert response.status_code == 200
    assert data["personal_username"] == "Dave"
    assert data["sympathy"] == "Barsik"
    assert data["sex"] is None


def test_delete_hero(session: Session, client: TestClient, create_user: User):
    session.add(create_user)
    session.commit()
    response = client.delete(f"/users/{create_user.id}")
    data = response.json()
    user_in_db = session.get(User, create_user.id)
    assert response.status_code == 200
    assert data['ok'] == True
    assert user_in_db is None
