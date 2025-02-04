from fastapi import FastAPI, HTTPException, status, Request
from routers.pages import router as pages_router
from routers.safety import router as safety_router
from routers.db import router as db_router
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from fastapi.responses import Response

app = FastAPI()

# origins = [
#     'http://127.0.0.1:8000',
#     'http://127.0.0.1'
# ]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_headers=['*']
# )

app.include_router(pages_router)
app.include_router(safety_router)
app.include_router(db_router)

app.mount("/", StaticFiles(directory="static_files"), name="static")


def app_context_401(request: Request) -> Dict[str, Any]:
    """
Функция процессор-контекста. Используется Jinja2 для вставки дополнительных данных на html-страницу. Таким образом,
превращая статическую страницу в динамическую.
    """
    return {"message": 'Пользователь не авторизован'}


def app_context_404(request: Request) -> Dict[str, Any]:
    """
Функция процессор-контекста. Используется Jinja2 для вставки дополнительных данных на html-страницу. Таким образом,
превращая статическую страницу в динамическую.
    """
    return {"message": 'Пользователь не найден'}


templates_401 = Jinja2Templates(directory='html_templates/', context_processors=[app_context_401])
templates_404 = Jinja2Templates(directory='html_templates/', context_processors=[app_context_404])


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == 401:
        return templates_401.TemplateResponse(
            request=request,
            name="fail_oauth.html",
            status_code=exc.status_code,
            headers=exc.headers,
        )
    if exc.status_code == 404:
        return templates_404.TemplateResponse(
            request=request,
            name="fail_oauth.html",
            status_code=exc.status_code,
            headers=exc.headers,
        )