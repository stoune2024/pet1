from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from .safety import verify_token, TokenData
from fastapi.staticfiles import StaticFiles
from os.path import relpath
from .fake_no_sql_db import *

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
        "title": index_page['title'],
        "header": index_page['header']
    })


@router.get('/barsik', response_class=HTMLResponse)
async def get_barsik_page(request: Request):
    """ Эндпоинт отображения раздела про Барсика """
    return templates.TemplateResponse(request=request, name="barsik.html", context={
        "title": barsik_page['title'],
        "header": barsik_page['header']
    })


@router.get('/marsik', response_class=HTMLResponse)
async def get_marsik_page(request: Request):
    """ Эндпоинт отображения раздела про Марсика """
    return templates.TemplateResponse(request=request, name="marsik.html", context={
        "title": marsik_page['title'],

    })


@router.get('/bonus', response_class=HTMLResponse)
def get_bonus_page(
        request: Request,
        user_token: Annotated[TokenData, Depends(verify_token)],
):
    """ Эндпоинт просмотра раздела, требующего авторизации """
    if user_token:
        return templates.TemplateResponse(request=request, name="bonus.html")
    # return templates.TemplateResponse(request=request, name="fail_oauth.html")


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
    context = {"username": user_token.username}
    return templates.TemplateResponse(request=request, name="suc_oauth.html", context=context)

