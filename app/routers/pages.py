from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Annotated
from .db import User
from fastapi.security import OAuth2PasswordBearer
from .safety import verify_token, TokenData
from fastapi.staticfiles import StaticFiles
from os.path import relpath


router = APIRouter(tags=['Фронтенд'])

templates = Jinja2Templates(directory=['html_templates', 'app/html_templates'])

router.mount('/static_files', StaticFiles(directory=relpath(f'{relpath(__file__)}/../../static_files')), name='static')



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get('/', response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@router.get('/barsik', response_class=HTMLResponse)
async def get_barsik_page(request: Request):
    return templates.TemplateResponse(request=request, name="barsik.html")


@router.get('/marsik', response_class=HTMLResponse)
async def get_marsik_page(request: Request):
    return templates.TemplateResponse(request=request, name="marsik.html")


@router.get('/bonus', response_class=HTMLResponse)
def get_bonus_page(
        request: Request,
        user_token: Annotated[TokenData, Depends(verify_token)],
):
    if user_token:
        return templates.TemplateResponse(request=request, name="bonus.html")
    # return templates.TemplateResponse(request=request, name="fail_oauth.html")


@router.get('/oauth', response_class=HTMLResponse)
async def get_oauth_page(request: Request):
    return templates.TemplateResponse(request=request, name="oauth.html")


@router.get('/reg', response_class=HTMLResponse)
async def get_reg_page(request: Request):
    return templates.TemplateResponse(request=request, name="reg.html")


@router.get('/suc_oauth', response_class=HTMLResponse)
async def get_suc_oauth_page(
        request: Request,
        user_token: Annotated[TokenData, Depends(verify_token)]
):
    context = {
        "username": user_token.username
    }
    return templates.TemplateResponse(request=request, name="suc_oauth.html", context=context)
