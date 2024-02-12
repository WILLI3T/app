import sys
sys.path.append('..')
from starlette.responses import RedirectResponse
from fastapi import Depends, HTTPException, status, APIRouter, Request, Response, Form
from typing import Optional
from app import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    prefix="/auth2",
    tags=["auth2"],
    responses={401: {"description": "Not authorized"}},
)

class LoginForm:
    def __init__(self, request: Request):
        self.request = request
        self.errors = []
        self.username: Optional[str] = None
        self.password: Optional[str] = None
    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.User)\
        .filter(models.User.username == username)\
        .first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int,
                        expires_delta: Optional[timedelta] = None):

    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request):

    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            logout(request)
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="Not Found")



@router.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username,
                                user.id,
                                expires_delta=token_expires)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return True

@router.get("/", response_class=HTMLResponse)
async def authpage(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/boxes", status_code=status.HTTP_302_FOUND)
        validate_user_cookie = await login_for_access_token(response=response, form_data = form,db=db)

        if not validate_user_cookie:
            msg = "Invalid username or password"
            return templates.TemplateResponse("login2.html", {"request": request, "msg": msg})
        return response
    except HTTPException:
        msg = "Unknow error"
        return templates.TemplateResponse("login2.html", {"request": request, "msg": msg})

@router.get("/logout")
async def logout(request: Request):
    msg = "Logout Successfull"
    response = templates.TemplateResponse("login2.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    return response



@router.get("/register", response_class=HTMLResponse)
async def register (request: Request):
    return templates.TemplateResponse("register2.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, username: str = Form(...), role: str = Form(...),
                        email: str = Form(...), isactive: str = Form(...), password: str = Form(...),
                        password2: str = Form(...), db: Session = Depends(get_db)):
    validation1 = db.query(models.Users).filter(models.Users.username == username).first()

    if password != password2 or validation1 is not None:
        msg = "Invalid registration request"
        return templates.TemplateResponse("register2.html", {"request": request, "msg": msg})

    isactive = bool(isactive)

    user_model = models.User()
    user_model.username = username
    user_model.email = email
    user_model.is_active = isactive

    hash_password = get_password_hash(password)
    user_model.password_hash = hash_password

    db.add(user_model)
    db.commit()

    id_user = db.query(models.User).filter(models.User.username == username).first().user_id
    user_role_model = models.UserRole()
    
    id_role = db.query(models.Role).filter(models.Role.role_name == role).first().role_id    
    user_role_model.user_id = id_user
    user_role_model.role_id = id_role

    
    db.add(user_role_model)
    db.commit()
    

    msg= "User created successfully"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

