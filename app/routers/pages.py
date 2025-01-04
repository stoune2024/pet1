from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(tags=['Фронтенд'])

templates = Jinja2Templates(directory='html_templates/')


@router.get('/')
async def get_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
