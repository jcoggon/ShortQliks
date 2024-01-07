import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession
from app import Base
from app.models.qlik_item import QlikItem  # Import the QlikItem model

# Create an instance of the async engine
engine = create_async_engine('postgresql+asyncpg://qlikuser:qlikpassword@postgres:5432/qlikdb')

async def create_tables():
    async with engine.begin() as conn:
        # Create all tables in the database which are defined by Base's subclasses
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully!")

# Run the function using an event loop
asyncio.run(create_tables())