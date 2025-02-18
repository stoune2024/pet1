from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from app.main import app
# from app.routers.db import get_session

client = TestClient(app)


def test_create_hero():
    engine = create_engine(
        "sqlite:///tests/testing.db", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        def get_session_override():
            return session
        print('до переписи')
        app.dependency_overrides[get_session] = get_session_override
        print('после переписи')
        # client = TestClient(app)
        response = client.post(
            "/heroes/", json={"name": "Deadpond", "secret_name": "Dive Wilson"}
        )
        app.dependency_overrides.clear()
        data = response.json()
        assert response.status_code == 200
        # assert data["name"] == "Deadpond"
        # assert data["secret_name"] == "Dive Wilson"
        # assert data["age"] is None
        # assert data["id"] is not None
