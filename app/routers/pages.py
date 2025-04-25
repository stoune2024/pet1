from fastapi import APIRouter, Request, Depends, Response, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from .safety import verify_token, TokenData, get_user, SessionDep, pwd_context
from fastapi.staticfiles import StaticFiles
from os.path import relpath
from .no_sql_db import redis_client
from .db import User, UserUpdate

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
        return templates.TemplateResponse(request=request, name='index.html', context={
            "title": redis_client.get('index_page_verif'),
            "header": redis_client.hget('index_page', 'header'),
            "nav": redis_client.lrange('index_page_nav_verif', 0, -1),
            "header2": redis_client.hget('index_page', 'header2'),
            "p1": redis_client.hget('index_page', 'p1'),
            "p2": redis_client.hget('index_page', 'p2'),
            "about": redis_client.lrange('index_page_about', 0, -1)

        })
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
    token = request.cookies.get('access-token')
    if token:
        return templates.TemplateResponse(request=request, name="index.html", context={
            "title": redis_client.hget('barsik_page', 'title'),
            "header": redis_client.hget('barsik_page', 'header'),
            "nav": redis_client.lrange('barsik_page_nav_verif', 0, -1),
            "header2": redis_client.hget('barsik_page', 'header2'),
            "p1": redis_client.hget('barsik_page', 'p1'),
            "p2": redis_client.hget('barsik_page', 'p2'),
            "about": redis_client.lrange('barsik_page_about', 0, -1)
        })
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
    token = request.cookies.get('access-token')
    if token:
        return templates.TemplateResponse(request=request, name="index.html", context={
            "title": redis_client.hget('marsik_page', 'title'),
            "header": redis_client.hget('marsik_page', 'header'),
            "nav": redis_client.lrange('marsik_page_nav_verif', 0, -1),
            "header2": redis_client.hget('marsik_page', 'header2'),
            "p1": redis_client.hget('marsik_page', 'p1'),
            "p2": redis_client.hget('marsik_page', 'p2'),
            "about": redis_client.lrange('marsik_page_about', 0, -1)
        })
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


@router.get('/log_out', response_class=HTMLResponse)
async def log_out(
        request: Request,
        response: Response
):
    response = templates.TemplateResponse(request=request, name='notification.html', context={
        "message": redis_client.get('log_out_message')
    })
    response.delete_cookie(key='access-token')
    return response


@router.get('/settings', response_class=HTMLResponse)
async def get_settings_page(
        request: Request,
        user_token: Annotated[TokenData, Depends(verify_token)],
        session: SessionDep):
    user = get_user(user_token.username, session)
    if user_token:
        return templates.TemplateResponse(request=request, name='index.html', context={
            "title": redis_client.get('settings_title'),
            "header": redis_client.get('settings_title'),
            "nav": redis_client.lrange('settings_page_nav_verif', 0, -1),
            "username": user.username,
            "usermail": user.usermail,
            "personal_username": user.personal_username,
            "sex": user.sex,
            "birthdate": user.birthdate,
            "sympathy": user.sympathy,
            "about": redis_client.lrange('settings_page_about', 0, -1),
            "user_id": user.id,
        })


@router.get('/settings_update')
async def get_settings_update_page(
        request: Request,
        user_token: Annotated[TokenData, Depends(verify_token)],
        session: SessionDep
):
    user = get_user(user_token.username, session)
    if user_token:
        return templates.TemplateResponse(request=request, name='index.html', context={
            "title": redis_client.get('settings_update_title'),
            "header": redis_client.get('settings_update_title'),
            "nav": redis_client.lrange('settings_page_nav_verif', 0, -1),
            "about": redis_client.lrange('settings_page_about', 0, -1),
            "username": user.username,
            "usermail": user.usermail,
            "personal_username": user.personal_username,
            "birthdate": user.birthdate,
            "user_id": user.id,
            "sympathy": user.sympathy,
        })


@router.post("/users/{user_id}")
def update_user(
        user_id: int,
        user: Annotated[UserUpdate, Form()],
        session: SessionDep,
        request: Request
):
    """
Функция обновления данных конкретного пользователя в БД. Является альтернативой
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
    return templates.TemplateResponse(request=request, name="notification.html", context={
        "message": redis_client.get('settings_changed')
    })

