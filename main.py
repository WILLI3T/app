from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import paramiko
from paramiko import RSAKey
from app import models
from app.routers import auth, auth2, boxes, box
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_root():
    return RedirectResponse(url="/boxes", status_code=status.HTTP_302_FOUND)

app.include_router(auth.router)
app.include_router(auth2.router)
app.include_router(boxes.router)
app.include_router(box.router)
