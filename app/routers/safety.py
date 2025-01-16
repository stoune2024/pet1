from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


router = APIRouter(tags=['Безопасность'])

#Авторизация пользователя
# @router.post('/oauth/auth', response_class=HTMLResponse)
# async def authorization(data:FormData):
#     pass