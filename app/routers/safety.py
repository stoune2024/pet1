from fastapi import APIRouter
from passlib.context import CryptContext
from db import read_one_user

# Контекст PassLib. Используется для хэширования и проверки паролей.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    user = read_one_user(username)
    return user



def authenticate_user(fake_db, username: str, password: str):
    """
Функция аутентификации и возврата пользователя
    :param fake_db: База данных
    :param username: Имя пользователя для аутентификации по логину
    :param password: Пароль пользователя для аутентификации по паролю
    :return: Пользователь (запись из БД)
    """
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
