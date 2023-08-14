
from dotenv import load_dotenv
load_dotenv()


import logging
from logging.handlers import RotatingFileHandler

# Configure logging
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler('/mnt/data/ShortQliks_new_unzipped/ShortQliks/logs/shortqliks.log', mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

logger.info('ShortQliks application started')


from fastapi import FastAPI, Request
from routes import dashboard_routes

app = FastAPI()

logger = logging.getLogger(__name__)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"Error occurred: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    logger.error(f"Unexpected error occurred: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )

# TODO: Add other routes and application logic here

# Including the dashboard routes
app.include_router(dashboard_routes.router)
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional

# Security utilities
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # Example secret key, change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class User(BaseModel):
    email: str
    password: str

class UserInDB(User):
    hashed_password: str

# Placeholder user database, replace with actual database operations
fake_users_db = {
    "test@example.com": {
        "email": "test@example.com",
        "hashed_password": pwd_context.hash("password123"),
        "api_key": "example_api_key"
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, email: str):
    user = db.get(email)
    if user:
        return UserInDB(**user)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register")
async def register_user(user: User, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    new_user = create_user(db, user)
    return {"email": new_user.email, "api_key": new_user.api_key}

    user = get_user(fake_users_db, form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register")
async def register_user(user: User):
    # Placeholder registration logic, replace with actual database operations
    if user.email in fake_users_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    fake_users_db[user.email] = {
        "email": user.email,
        "hashed_password": get_password_hash(user.password),
        "api_key": "generated_api_key"  # Placeholder API key generation logic
    }
    return {"email": user.email, "api_key": "generated_api_key"}

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Database configurations
DATABASE_URL = os.environ.get('DATABASE_URI', 'postgresql://username:password@db:5432/dbname')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# User Model
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    api_key = Column(String, nullable=True)

    tenants = relationship("TenantDB", back_populates="owner")

# Tenant Model
class TenantDB(Base):
    __tablename__ = "tenants"

    tenant_id = Column(Integer, primary_key=True, index=True)
    tenant_name = Column(String, index=True, nullable=False)
    qlik_cloud_key = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("UserDB", back_populates="tenants")

# Tasks Model
class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey('tenants.tenant_id'))
    title = Column(String, index=True, nullable=False)
    status = Column(String, nullable=True)

    owner = relationship("TenantDB", back_populates="tenants")

# CRUD operations for users

def create_user(db: Session, user: User):
    db_user = UserDB(email=user.email, hashed_password=get_password_hash(user.password), api_key="generated_api_key")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(UserDB).filter(UserDB.email == email).first()

# Data models for tenants

class Tenant(BaseModel):
    tenant_name: str
    qlik_cloud_key: str

class TenantInDB(Tenant):
    tenant_id: int

# CRUD operations for tenants

def create_tenant(db: Session, tenant: Tenant, user_id: int):
    db_tenant = TenantDB(**tenant.dict(), user_id=user_id)
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant

def get_tenants_by_user(db: Session, user_id: int):
    return db.query(TenantDB).filter(TenantDB.user_id == user_id).all()

@app.post("/add-tenant", response_model=TenantInDB)
async def add_tenant(tenant: Tenant, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_tenant(db=db, tenant=tenant, user_id=current_user.id)

@app.get("/list-tenants", response_model=List[TenantInDB])
async def list_tenants(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_tenants_by_user(db, user_id=current_user.id)

@app.get("/dashboard")
async def dashboard_page(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tenants = get_tenants_by_user(db, user_id=current_user.id)
    return templates.TemplateResponse("dashboard.html", {"request": request, "tenants": tenants})

@app.get("/add-tenant-page")
async def add_tenant_page():
    return templates.TemplateResponse("add_tenant.html", {"request": request})

# CRUD operations for editing and deleting tenants

def edit_tenant(db: Session, tenant_id: int, tenant: Tenant):
    db_tenant = db.query(TenantDB).filter(TenantDB.tenant_id == tenant_id).first()
    if not db_tenant:
        return None
    for key, value in tenant.dict().items():
        setattr(db_tenant, key, value)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant

def delete_tenant(db: Session, tenant_id: int):
    db_tenant = db.query(TenantDB).filter(TenantDB.tenant_id == tenant_id).first()
    if not db_tenant:
        return None
    db.delete(db_tenant)
    db.commit()
    return db_tenant

# Routes for editing and deleting tenants

@app.put("/edit-tenant/{tenant_id}", response_model=TenantInDB)
async def edit_tenant_endpoint(tenant_id: int, tenant: Tenant, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated_tenant = edit_tenant(db, tenant_id, tenant)
    if not updated_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return updated_tenant

@app.delete("/delete-tenant/{tenant_id}")
async def delete_tenant_endpoint(tenant_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deleted_tenant = delete_tenant(db, tenant_id)
    if not deleted_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"detail": "Tenant deleted successfully"}

@app.get("/edit-tenant-page/{tenant_id}")
async def edit_tenant_page(tenant_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tenant = db.query(TenantDB).filter(TenantDB.tenant_id == tenant_id).first()
    if not tenant or tenant.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return templates.TemplateResponse("edit_tenant.html", {"request": request, "tenant_id": tenant.tenant_id, "tenant_name": tenant.tenant_name, "qlik_cloud_key": tenant.qlik_cloud_key})
