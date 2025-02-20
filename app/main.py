from fastapi import FastAPI, HTTPException, status, Request
from routers.pages import router as pages_router
from routers.pages import templates
from routers.safety import router as safety_router, verify_token, TokenData
from routers.db import router as db_router, get_session, UserCreate, User, pwd_context, UserUpdate, UserPublic
from fastapi.staticfiles import StaticFiles
from os.path import realpath, relpath

# from contextlib import asynccontextmanager
# from sqlmodel import SQLModel, create_engine


app = FastAPI()

app.include_router(pages_router)
app.include_router(safety_router)
app.include_router(db_router)

app.mount('/static_files', StaticFiles(directory=relpath(f'{relpath(__file__)}/../static_files')), name='static')


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
