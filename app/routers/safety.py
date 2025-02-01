from fastapi import APIRouter, HTTPException, status, Depends, Request
from passlib.context import CryptContext
from sqlmodel import create_engine, Session, select, SQLModel
from .db import User, UserPublic
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import jwt
from typing import Annotated, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from jwt.exceptions import InvalidTokenError
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from starlette.status import HTTP_401_UNAUTHORIZED

templates = Jinja2Templates(directory='html_templates/')

SECRET_KEY = "d07ee9a686027cc593ced3e2a87eebc53697ca6efc3ac1a640afd0158035d714"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Модель для ответа на запрос на получения токена
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
                    raise credentials_exception
                else:
                    return None
            return param
        token = request.cookies.get('access-token')
        if token:
            param = token
            return param
        else:
            print('ошабка тут')
            raise credentials_exception


class HTTPExceptionWithResponse(HTTPException):
    async def __call__(self, request: Request):
        pass
        # return templates.TemplateResponse(request=request, name="fail_oauth.html")
        # redirect_url = "/fail_oauth"
        # response = RedirectResponse(
        #     redirect_url, status_code=status.HTTP_401_UNAUTHORIZED
        # )
        # return response


# Контекст PassLib. Используется для хэширования и проверки паролей.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")

sqlite_file_name = "../database.db"

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


async def verify_token(
        token: Annotated[str, Depends(oauth2_scheme)],
        request: Request
):
    """
    Функция проверки JWT-токена пользователя и возврата пользователя, если все в порядке. Функция получает
    токен из класса OAuth2PasswordBearer. Данная функция не работает на клиенте, только в Swagger UI.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        print('ошибка 2')
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return token_data


@router.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@router.post("/login")
async def validate_login_form(
        request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
Эндпоинт отвечает за обработку данных, пришедших из формы авторизации. Если пользователь успешно прошел
аутентификацию и авторизацию JWT-токен сохраняется в куках. Происходит перенаправление на другую страницу.

    """
    token = await login_for_access_token(request, form_data)
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
):
    """
Эндпоинт отвечает за аутентификацию пользователя и генерацию JWT-токена. Функция работает как зависимость
в эндпоинте POST /login

    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise credentials_exception
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}