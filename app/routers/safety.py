from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from functools import lru_cache

import jwt
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.exc import InvalidRequestError
from sqlmodel import create_engine, Session, select, SQLModel

from .db import User
from .. import config

templates = Jinja2Templates(directory=['html_templates', 'app/html_templates', '../app/html_templates'])


@lru_cache
def get_settings():
    return config.Settings()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    """ Расширяет функционал класса OAuth2PasswordBearer с целью получения JWT-токена из Cookie"""

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        if authorization is not None:
            scheme, param = get_authorization_scheme_param(authorization)
            if not authorization or scheme.lower() != "bearer":
                if self.auto_error:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Could not find Authorization header",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                else:
                    return None
            return param
        token = request.cookies.get('access-token')
        if token:
            param = token
            return param
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not find token",
                headers={"WWW-Authenticate": "Bearer"},
            )


# Контекст PassLib. Используется для хэширования и проверки паролей.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")

sqlite_file_name = "database.db"

sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_password_hash(password):
    """
    :param password: Пароль, поступающий от пользователя
    :return: Хешированный пароль пользователя
    """
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """
Функция проверки соответствия полученного пароля и хранимого хеша
    :param plain_password: Полученный пароль
    :param hashed_password: Хранимый хеш
    :return: Истина или ложь в зависимости от параметров
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str, session: SessionDep):
    """
Функция получения информации о пользователе из БД
    :param session: Текущая сессия
    :param username: Логин для получения по нему
    :return: Запись о пользователе из БД
    """
    try:
        print(username)
        user = session.exec(select(User).where(User.username == username)).one()
        return user
    except InvalidRequestError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )


def authenticate_user(username: str, password: str, session: SessionDep):
    """
Функция аутентификации и возврата пользователя
    :param username: Логин пользователя
    :param password: Пароль пользователя для аутентификации по паролю
    :return: Пользователь (запись из БД)
    """
    user = get_user(username, session)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
        settings: Annotated[config.Settings, Depends(get_settings)],
        data: dict,
        expires_delta: timedelta | None = None,
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


async def verify_token(
        settings: Annotated[config.Settings, Depends(get_settings)],
        token: Annotated[str, Depends(oauth2_scheme)],
        request: Request,
        session: SessionDep
):
    """ Функция проверки JWT-токена пользователя и возврата токена с username пользователя, если все в порядке. """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not find token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user(token_data.username, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not find user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data


@asynccontextmanager
async def lifespan(router: APIRouter):
    create_db_and_tables()
    yield


router = APIRouter(tags=['Безопасность'], lifespan=lifespan)


@router.post("/login")
async def validate_login_form(
        request: Request,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: SessionDep,
        settings: Annotated[config.Settings, Depends(get_settings)]
):
    """
Эндпоинт отвечает за обработку данных, пришедших из формы авторизации. Если пользователь успешно прошел
аутентификацию и авторизацию JWT-токен сохраняется в куках. Происходит перенаправление на другую страницу.

    """
    token = await login_for_access_token(request, form_data, session, settings)
    access_token = token.get("access_token")
    redirect_url = "/suc_oauth"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = RedirectResponse(
        redirect_url, status_code=status.HTTP_303_SEE_OTHER, headers=headers
    )
    response.set_cookie(
        key='access-token', value=access_token, httponly=True, secure=True)
    return response


@router.post("/token")
async def login_for_access_token(
        request: Request,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: SessionDep,
        settings: Annotated[config.Settings, Depends(get_settings)]
):
    """
Эндпоинт отвечает за аутентификацию пользователя и генерацию JWT-токена. Функция работает как зависимость
в эндпоинте POST /login

    """
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not find user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        settings,
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


