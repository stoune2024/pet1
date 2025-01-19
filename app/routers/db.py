import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request
from sqlmodel import SQLModel, create_engine, Session, Field
from pydantic import EmailStr
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='html_templates/')

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    usermail: EmailStr | None = Field(default=None)
    personal_username: str | None = None
    sex: str | None = None
    birthdate: datetime.date | None = None
    sympathy: str | None = None
    password: str


sqlite_file_name = "../database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(tags=['База данных'])


@router.on_event("startup")
def on_startup():
    create_db_and_tables()


# Регистрация пользователя
@router.post("/reg", response_class=HTMLResponse)
def create_user(user: Annotated[User, Form()], session: SessionDep, request: Request):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return templates.TemplateResponse(request=request, name="suc_reg.html")
