import sys

from starlette.responses import RedirectResponse

sys.path.append("..")
from starlette import status
from fastapi import Depends, HTTPException, APIRouter, Request, Form
from sqlalchemy.orm import Session
from .auth import get_current_user
from app import models
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database import SessionLocal, engine

router = APIRouter(
    prefix="/boxes",
    tags=["boxes"],
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
    boxes = db.query(models.Box).all()
    return templates.TemplateResponse("home.html", {"request": request, "boxes": boxes, "user": user})

@router.get("/box/{numer}", response_class=HTMLResponse)
async def get_profile(request: Request, db: Session = Depends(get_db)):
    # Get the current user
    current_user = await get_current_user(request)
    if current_user is None:
        raise HTTPException(status_code=404, detail="Not Found")

    # Return the user's data
    return templates.TemplateResponse("box.html")