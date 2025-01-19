from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter(tags=['Фронтенд'])

templates = Jinja2Templates(directory='html_templates/')


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
async def get_bonus_page(request: Request):
    return templates.TemplateResponse(request=request, name="bonus.html")


@router.get('/oauth', response_class=HTMLResponse)
async def get_oauth_page(request: Request):
    return templates.TemplateResponse(request=request, name="oauth.html")


@router.get('/reg', response_class=HTMLResponse)
async def get_reg_page(request: Request):
    return templates.TemplateResponse(request=request, name="reg.html")
