from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import Config  # Adjust the import path based on your project structure
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

# Get the database URL from your config (you may need to adjust the import path)
DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI

# Create an async database engine and session
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Create a regular database engine for synchronous operations
sync_engine = create_engine(DATABASE_URL)

# Create a declarative base for your models
Base = declarative_base()

# Create a FastAPI app
app = FastAPI()

@app.on_event("startup")
async def startup():
    # Initialize the database connection pool
    await engine.connect()

@app.on_event("shutdown")
async def shutdown():
    # Close the database connection pool when the application shuts down
    await engine.disconnect()

# Include routers (FastAPI's equivalent of blueprints)
from app.main.routes import router as main_router  # Adjust the import path
app.include_router(main_router)
