from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import Config  # Ensure the correct import path based on your project structure
from sqlalchemy.ext.declarative import declarative_base
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

# Get the database URL from your config
DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI

# Create an async database engine and session
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Create a declarative base for your models
Base = declarative_base()

# Create a FastAPI app
app = FastAPI()

@app.on_event("startup")
async def startup():
    # Initialize the database connection pool
    await engine.connect()

# Uncomment if you want to handle shutdown event
@app.on_event("shutdown")
async def shutdown():
    # Close the database connection pool when the application shuts down
    await engine.disconnect()
    
@app.exception_handler(ValidationError)
async def handler1(request: Request, exc: Exception):
    print("ValidationError")
    print(type(exc))
    return JSONResponse(str(exc))


@app.exception_handler(RequestValidationError)
async def handler2(request: Request, exc: Exception):
    print("RequestValidationError")
    print(type(exc))
    return JSONResponse(str(exc))


@app.exception_handler(Exception)
async def handler3(request: Request, exc: Exception):
    print("Exception")
    print(type(exc))
    return JSONResponse(str(exc))

# Include routers (FastAPI's equivalent of blueprints)
from app.main.routes import router as main_router
from app.main.user_routes.app_search_routes import router as app_search_router
from app.main.user_routes.create_tenant_routes import router as create_tenant_router
from app.main.user_routes.signup_routes import router as signup_router
from app.main.user_routes.onboard_routes import router as onboard_router
from app.main.qlik_routes.fetch_and_store_apps_routes import router as app_store_router
from app.main.qlik_routes.fetch_and_store_spaces_routes import router as space_store_router
from app.main.qlik_routes.fetch_and_store_users_routes import router as user_store_router
from app.main.qlik_routes.fetch_and_store_reload_tasks_routes import router as reload_tasks_router

app.include_router(main_router)
app.include_router(app_search_router, prefix="/api", tags=["App Search"])
app.include_router(create_tenant_router, prefix="/api", tags=["Create Tenant"])
app.include_router(signup_router, prefix="/api", tags=["Signup User"])
app.include_router(onboard_router, prefix="/api", tags=["Onboard User"])
app.include_router(app_store_router, prefix="/api", tags=["Store Apps"])
app.include_router(space_store_router, prefix="/api", tags=["Store Spaces"])
app.include_router(user_store_router, prefix="/api", tags=["Store Users"])
app.include_router(reload_tasks_router, prefix="/api", tags=["Store Reload Tasks"])
