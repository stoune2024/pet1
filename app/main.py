from fastapi import FastAPI
from routers.pages import router as pages_router
from routers.safety import router as safety_router
from routers.db import router as db_router
from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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
