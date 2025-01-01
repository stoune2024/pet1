from fastapi import FastAPI, Depends
# from frontend_files import *
from fastapi.responses import HTMLResponse
from typing import Annotated
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/", StaticFiles(directory="frontend_files", html=True), name="/")