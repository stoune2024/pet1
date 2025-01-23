from fastapi import APIRouter, HTTPException, status, Depends
from passlib.context import CryptContext
from sqlmodel import create_engine, Session, select
from .db import User
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import jwt
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

SECRET_KEY = "d07ee9a686027cc593ced3e2a87eebc53697ca6efc3ac1a640afd0158035d714"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Модель для ответа на запрос на получения токена
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# Контекст PassLib. Используется для хэширования и проверки паролей.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

sqlite_file_name = "../../database.db"

sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

router = APIRouter(tags=['Безопасность'])


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


def get_user(username: str):
    """
Функция получения информации о пользователе из БД
    :param username: Логин для получения по нему
    :return: Запись о пользователе из БД
    """
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).one()
        return user


def authenticate_user(username: str, password: str):
    """
Функция аутентификации и возврата пользователя
    :param username: Логин пользователя
    :param password: Пароль пользователя для аутентификации по паролю
    :return: Пользователь (запись из БД)
    """
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Функция проверки JWT-токена пользователя и возврата пользователя, если все в порядке
    :param token: JWT-токен пользователя
    :return: Пользователь
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# @router.post("/oauth/auth")
# async def login_for_access_token(
#         form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
# ) -> Token:
#     """
# Функиця создания JWT-токена
#     :param form_data: Форма авторизации, заполняемая пользователем
#     :return: JWT-токен
#     """
#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return Token(access_token=access_token, token_type="bearer")
