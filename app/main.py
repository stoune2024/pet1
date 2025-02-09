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

templates = Jinja2Templates(directory='html_templates/')


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == 401:
        message = "Пользователь не авторизован"
        return templates.TemplateResponse(
            request=request,
            name="fail_oauth.html",
            status_code=exc.status_code,
            headers=exc.headers,
            context={"message": message}
        )
    if exc.status_code == 404:
        message = "Пользователь не найден"
        return templates.TemplateResponse(
            request=request,
            name="fail_oauth.html",
            status_code=exc.status_code,
            headers=exc.headers,
            context={"message": message}
        )
