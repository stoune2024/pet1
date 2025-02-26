import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request, Query, HTTPException, Body
from sqlmodel import SQLModel, create_engine, Session, Field, select
from pydantic import EmailStr
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from contextlib import asynccontextmanager
from os.path import relpath
from fastapi.staticfiles import StaticFiles
from .fake_no_sql_db import successful_registration_page

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

templates = Jinja2Templates(directory=['html_templates', 'app/html_templates', '../app/html_templates'])


class UserBase(SQLModel):
    usermail: EmailStr | None = Field(default=None)
    personal_username: str | None = None
    sex: str | None = None
    birthdate: datetime.date | None = None
    sympathy: str | None = None


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    hashed_password: str


class UserPublic(UserBase):
    id: int


class UserCreate(UserBase):
    username: str
    password: str


class UserUpdate(UserBase):
    username: str | None = None
    password: str | None = None


sqlite_file_name = "../database.db"

sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(router: APIRouter):
    create_db_and_tables()
    yield


router = APIRouter(tags=['База данных'], lifespan=lifespan)

router.mount('/static_files', StaticFiles(directory=relpath(f'{relpath(__file__)}/../../static_files')), name='static')


@router.post("/reg/", response_class=HTMLResponse)
def create_user(user: Annotated[UserCreate, Form()], session: SessionDep, request: Request):
    """
Функция создает пользователя и добавляет его в базу данных.
    :param user: Объект модели User
    :param session: Сессия
    :param request: Запрос. Требуется для Jinja2 для создания шаблона
    :return: Шаблон Jinja2, говорящий об успешной регистрации
    """
    hashed_password = pwd_context.hash(user.password)
    extra_data = {"hashed_password": hashed_password}
    db_user = User.model_validate(user, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return templates.TemplateResponse(request=request, name="notification.html", context={
        "message": successful_registration_page['message']
    })


# Работает. Не реализована
@router.get("/users/", response_model=list[UserPublic])
def read_users(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
):
    """
Функция получения списка всех пользователей со всеми полями. Функция работает, но пока не реализована на практике.
    :param session: Сессия
    :param offset: Отступ
    :param limit: Лимит
    :return: Список пользователей без пароля
    """
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


# Работает. Не реализована
@router.patch("/users/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user: Annotated[UserUpdate, Form()], session: SessionDep):
    """
Функция обновления данных конкретного пользователя в БД. Функция работает, но пока не реализована на практике.
    :param user_id: Параметр пути, в то же время являющийся id в БД
    :param user: Тело запроса с данными для обновления
    :param session: Сессия
    :return: Обновленный пользователь
    """
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="Oops.. User not found")
    user_data = user.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = pwd_context.hash(password)
        extra_data["hashed_password"] = hashed_password
    user_db.sqlmodel_update(user_data, update=extra_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


# Работает, не реализована
@router.delete("/users/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    """
Функция удаления пользователя из БД. Функция работает, но пока не реализована на практике.
    :param user_id: Параметр пути, в то же время являющийся id в БД
    :param session: Сессия
    :return: Подтверждение удаления
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Oops.. User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}
