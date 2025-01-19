from fastapi import FastAPI
from routers.pages import router as pages_router
from routers.safety import router as safety_router
from routers.db import router as db_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost",
    "http://127.0.0.1;:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(pages_router)
app.include_router(safety_router)
app.include_router(db_router)

app.mount("/", StaticFiles(directory="static_files"), name="static")
