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
from routers.auth import get_password_hash, verify_password, get_current_user

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
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@router.get("/profile", response_class=HTMLResponse)
async def get_profile(request: Request, db: Session = Depends(get_db)):
    # Get the current user
    current_user = await get_current_user(request)
    if current_user is None:
        raise HTTPException(status_code=404, detail="Not Found")

    # Fetch the user's data from the database
    user_data = db.query(models.User).filter(models.User.user_id == current_user["id"]).first()

    # Fetch the user's roles from the database
    role_data = db.query(models.Role).join(models.UserRole).filter(models.UserRole.user_id == current_user["id"]).all()

    # Extract role names
    role_names = [role.role_name for role in role_data]

    # Return the user's data
    return templates.TemplateResponse("profile.html", {"request": request, "user": user_data, "roles": role_names})

@router.post("/set_new_password")
async def set_new_password(request: Request, current_password: str = Form(...), new_password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    authenticated_user = db.query(models.User).filter(models.User.user_id == user['id']).first()
    role_data = db.query(models.Role).join(models.UserRole).filter(models.UserRole.user_id == user["id"]).all()
    role_names = [role.role_name for role in role_data]
    
    if not verify_password(current_password, authenticated_user.password_hash):
        return templates.TemplateResponse("profile.html", {"request": request, "user": authenticated_user, "msg": "Incorrect current password", "roles": role_names})

    if new_password != confirm_password:
        return templates.TemplateResponse("profile.html", {"request": request, "user": authenticated_user, "msg": "New password and confirmation do not match", "roles": role_names})

    authenticated_user.password_hash = get_password_hash(new_password)
    db.commit()

    return templates.TemplateResponse("profile.html", {"request": request, "user": authenticated_user, "msg": "Password changed successfully", "roles": role_names})