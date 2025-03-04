from fastapi import FastAPI, HTTPException, status, Request
from app.routers.pages import router as pages_router, templates
from app.routers.safety import (router as safety_router,
                            verify_token,
                            TokenData,
                            OAuth2PasswordRequestForm,
                            authenticate_user,
                            get_user,
                            get_session as get_safety_session)
from app.routers.db import (router as db_router,
                        get_session as get_db_session,
                        UserCreate,
                        User,
                        pwd_context,
                        UserUpdate,
                        UserPublic)

from fastapi.staticfiles import StaticFiles
from os.path import realpath, relpath
from app.routers.fake_no_sql_db import *
from .routers.no_sql_db import redis_client

app = FastAPI()

app.include_router(pages_router)
app.include_router(safety_router)
app.include_router(db_router)

app.mount('/static_files', StaticFiles(directory=relpath(f'{relpath(__file__)}/../static_files')), name='static')


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == 401:
        return templates.TemplateResponse(
            request=request,
            name="notification.html",
            status_code=exc.status_code,
            headers=exc.headers,
            context={
                "message_401": redis_client.hget('failed_authorization_page', 'message_401')
            }
        )
    if exc.status_code == 404:
        return templates.TemplateResponse(
            request=request,
            name="notification.html",
            status_code=exc.status_code,
            headers=exc.headers,
            context={
                "message_404": redis_client.hget('failed_authorization_page', 'message_404')
            }
        )
