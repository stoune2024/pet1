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
