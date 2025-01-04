from fastapi import FastAPI
from routers.pages import router as pages_router
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.include_router(pages_router)

app.mount("/", StaticFiles(directory="static_files"), name="static")