import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, StaticPool, SQLModel, Session
from app.main import app, OAuth2PasswordRequestForm, authenticate_user, UserCreate, pwd_context, User
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
    class override_OAuth2PasswordRequestForm:
        def __init__(self, username: Annotated[str, Form()], password: Annotated[str, Form()]):
            self.username = username
            self.password = password

    app.dependency_overrides[OAuth2PasswordRequestForm] = override_OAuth2PasswordRequestForm

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


# app.dependency_overrides[OAuth2PasswordRequestForm] = override_OAuth2PasswordRequestForm
# app.dependency_overrides[authenticate_user] = override_authenticate_user
# app.dependency_overrides[get_user] = override_get_user

def test__login_for_access_token(session: Session,client: TestClient, create_user: User):
    session.add(create_user)
    session.commit()
    user_db = session.get(User, create_user.id)
    print(user_db)
    user_form_data = override_OAuth2PasswordRequestForm(username='fake_username', password='fake_password')

    response = client.post("/token", data={"username": user_form_data.username, "password": user_form_data.password})
    data = response.json()
    assert response.status_code == 200
    assert data['token_type'] == 'bearer'
