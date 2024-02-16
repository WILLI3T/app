import sys

from starlette.responses import RedirectResponse
import re
sys.path.append("..")
from starlette import status
from fastapi import Depends, HTTPException, APIRouter, Request, Form
from sqlalchemy.orm import Session
from .auth import get_current_user
from app import models
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database import SessionLocal, engine
from routers.auth import get_password_hash, verify_password, get_current_user
import paramiko
from paramiko import RSAKey
from paramiko.proxy import ProxyCommand

router = APIRouter(
    prefix="/serwis",
    tags=["serwis"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="app/templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request,db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("serwis.html", {"request": request, "user": user})

@router.get("/{device_name}", response_class=HTMLResponse)
async def read_all_by_user(request: Request,db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("pulpit.html", {"request": request, "user": user})

@router.get("/run-macio-read-box/{device_number}")
async def run_remote_script(device_number: int):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key_path = '/code/app/key/id_rsa_lede'
    mykey = paramiko.RSAKey.from_private_key_file(private_key_path)
    
    try:
        ssh.connect('a51.dacsystem.pl', username='devop', pkey=mykey)
        command = f'cd /home/devop/bilut/ && ./macio_read_box.sh {device_number}'
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read().decode('utf-8')
        ssh.close()

        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        result = ansi_escape.sub('', result)

        if not result:
            return {"error": "No result for this device number"}
        return {"result": result}
    except Exception as e:
        ssh.close()
        return {"error": str(e)}

@router.get("/run-check-connection/{device_number}")
async def run_remote_script(device_number: int):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key_path = '/code/app/key/id_rsa_lede'
    mykey = paramiko.RSAKey.from_private_key_file(private_key_path)
    device_suffix = f"{device_number:03}"
    target_host = f"10.202.1{device_suffix[:2]}.{device_suffix[2:]}"
    
    try:
        ssh.connect('a51.dacsystem.pl', username='devop', pkey=mykey)
        command = f'ping -c 3 {target_host}'
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read().decode('utf-8')  # Corrected here
        error = stderr.read().decode('utf-8')  # Read the error messages
        ssh.close()

        if error:  # If there are any error messages, return them
            return {"error": error}

        if not result:
            return {"error": "No result for this device number"}
        return {"result": result}
    except Exception as e:
        ssh.close()
        return {"error": str(e)}

@router.get("/run-rsync2/{device_number}")
async def run_remote_script(device_number: int):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key_path = '/code/app/key/id_rsa_lede'
    mykey = paramiko.RSAKey.from_private_key_file(private_key_path)
    
    try:
        ssh.connect('a51.dacsystem.pl', username='devop', pkey=mykey)
        command = f'cd /home/devop/bilut/ && ./rsync2.sh {device_number}'
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read().decode('utf-8')
        ssh.close()

        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        result = ansi_escape.sub('', result)

        if not result:
            return {"error": "No result for this device number"}
        return {"result": result}
    except Exception as e:
        ssh.close()
        return {"error": str(e)}