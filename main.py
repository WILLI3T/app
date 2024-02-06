from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import paramiko
from paramiko import RSAKey
from app import models
from app.routers import auth, auth2, boxes
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Funkcja do nawiązywania połączenia SSH i wykonania polecenia
def ssh_execute_command(host, port, username, command):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    private_key = RSAKey.from_private_key_file('/root/.ssh/id_rsa_lede')

    ssh_client.connect(hostname=host, port=port, username=username, pkey=private_key)

    stdin, stdout, stderr = ssh_client.exec_command(command)
    result = stdout.read().decode()
    ssh_client.close()
    
    return result

# Funkcja do przetwarzania wyników polecenia SSH
def parse_ssh_result(result):
    # Załóżmy, że wynik jest pojedynczym wierszem z wartościami oddzielonymi przecinkami
    columns = result.split(",")
    # Konwersja na słownik lub inny format, który jest użyteczny dla aplikacji
    return {"data": columns}

@app.get("/box/{numer}", response_class=HTMLResponse)
def read_box(request: Request, numer: int):
    ssh_command = "export PGHOST=127.0.0.1; export PGPORT=5432; export PGUSER=gios; psql -d logdb -c 'Select * from sku_gps_info limit 1'"
    ssh_result = ssh_execute_command('a51.dacsystem.pl', 22, 'devop', ssh_command)
    
    box_info = parse_ssh_result(ssh_result)

    if box_info is None:
        raise HTTPException(status_code=404, detail="Box not found")
    
    # W tym miejscu należy zaimplementować renderowanie HTML z użyciem `box_info`
    # Poniżej znajduje się przykładowy, uproszczony kod HTML
    html_content = f"<html><body><h1>Box {numer}</h1><p>Data: {box_info['data']}</p></body></html>"
    return HTMLResponse(content=html_content)


@app.get("/")
async def read_root():
    return RedirectResponse(url="/boxes", status_code=status.HTTP_302_FOUND)

app.include_router(auth.router)
app.include_router(auth2.router)
app.include_router(boxes.router)
