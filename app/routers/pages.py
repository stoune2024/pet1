from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from .safety import verify_token, TokenData
from fastapi.staticfiles import StaticFiles
from os.path import relpath
from .fake_no_sql_db import *
from .no_sql_db import redis_client

router = APIRouter(tags=['Фронтенд'])

templates = Jinja2Templates(directory=['html_templates', 'app/html_templates', '../app/html_templates'])

router.mount('/static_files', StaticFiles(directory=relpath(f'{relpath(__file__)}/../../static_files')), name='static')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get('/')
async def get_index(
        request: Request,
):
    """ Эндпоинт отображения главного раздела сайта """
    token = request.cookies.get('access-token')
    if token:
        return {"message": "Hello world!"}
    return templates.TemplateResponse(request=request, name="index.html", context={
        "title": redis_client.hget('index_page', 'title'),
        "header": redis_client.hget('index_page', 'header'),
        "nav": redis_client.lrange('index_page_nav', 0, -1),
        "header2": redis_client.hget('index_page', 'header2'),
        "p1": redis_client.hget('index_page', 'p1'),
        "p2": redis_client.hget('index_page', 'p2'),
        "about": redis_client.lrange('index_page_about', 0, -1)
    })


@router.get('/barsik', response_class=HTMLResponse)
async def get_barsik_page(request: Request):
    """ Эндпоинт отображения раздела про Барсика """
    return templates.TemplateResponse(request=request, name="index.html", context={
        "title": redis_client.hget('barsik_page', 'title'),
        "header": redis_client.hget('barsik_page', 'header'),
        "nav": redis_client.lrange('barsik_page_nav', 0, -1),
        "header2": redis_client.hget('barsik_page', 'header2'),
        "p1": redis_client.hget('barsik_page', 'p1'),
        "p2": redis_client.hget('barsik_page', 'p2'),
        "about": redis_client.lrange('barsik_page_about', 0, -1)
    })


@router.get('/marsik', response_class=HTMLResponse)
async def get_marsik_page(request: Request):
    """ Эндпоинт отображения раздела про Марсика """
    return templates.TemplateResponse(request=request, name="index.html", context={
        "title": redis_client.hget('marsik_page', 'title'),
        "header": redis_client.hget('marsik_page', 'header'),
        "nav": redis_client.lrange('marsik_page_nav', 0, -1),
        "header2": redis_client.hget('marsik_page', 'header2'),
        "p1": redis_client.hget('marsik_page', 'p1'),
        "p2": redis_client.hget('marsik_page', 'p2'),
        "about": redis_client.lrange('marsik_page_about', 0, -1)
    })


@router.get('/bonus', response_class=HTMLResponse)
def get_bonus_page(
        request: Request,
        user_token: Annotated[TokenData, Depends(verify_token)],
):
    """ Эндпоинт просмотра раздела, требующего авторизации """
    if user_token:
        return templates.TemplateResponse(request=request, name="index.html", context={
            "title": redis_client.hget('bonus_page', 'title'),
            "header": redis_client.hget('bonus_page', 'header'),
            "nav": redis_client.lrange('bonus_page_nav', 0, -1),
            "header2": redis_client.hget('bonus_page', 'header2'),
            "p1": redis_client.hget('bonus_page', 'p1'),
            "p2": redis_client.hget('bonus_page', 'p2'),
            "p3": redis_client.hget('bonus_page', 'p3'),
            "about": redis_client.lrange('bonus_page_about', 0, -1)
        })


@router.get('/oauth', response_class=HTMLResponse)
async def get_oauth_page(request: Request):
    """ Эндпоинт отображения окна аутентификации/авторизации с формой  """
    return templates.TemplateResponse(request=request, name="oauth.html")


@router.get('/reg', response_class=HTMLResponse)
async def get_reg_page(request: Request):
    """ Эндпоинт отображения окна регистрации с формой """
    return templates.TemplateResponse(request=request, name="reg.html")


@router.get('/suc_oauth', response_class=HTMLResponse)
async def get_suc_oauth_page(
        request: Request,
        user_token: Annotated[TokenData, Depends(verify_token)]
):
    """ Эндпоинт уведомления об успешной авторизации """
    return templates.TemplateResponse(request=request, name="notification.html", context={
        "message": redis_client.hget('successful_authorization_page', 'message')
    })

