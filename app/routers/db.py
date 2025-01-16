from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlmodel import SQLModel, create_engine, Session
from pydantic import EmailStr, Field


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str | None = None
    # usermail: EmailStr | None = Field(default=None)
    password: str
    personal_username: str | None = None
    sex: str | None = None
    # birthdate: datetime | None = None
    sympathy: str | None = None



sqlite_file_name = "../database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread":False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session())]


router = APIRouter(tags=['База данных'])


@router.on_event("startup")
def on_startup():
    create_db_and_tables()

# Регистрация пользователя
@router.post("/reg")
def create_user(user:User, session:SessionDep) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user