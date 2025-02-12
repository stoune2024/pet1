from fastapi import FastAPI, HTTPException, status, Request
from routers.pages import router as pages_router
from routers.pages import templates
from routers.safety import router as safety_router
from routers.db import router as db_router
from fastapi.staticfiles import StaticFiles
from os.path import realpath, relpath

app = FastAPI()

app.include_router(pages_router)
app.include_router(safety_router)
app.include_router(db_router)

# Форма записи параметра directory обусловлена требованием pytest.
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
