from fastapi import APIRouter, Depends
from sqlalchemy import create_engine, MetaData, Table, select, and_, func
from sqlalchemy.orm import sessionmaker, registry
from sqlalchemy.ext.asyncio import AsyncSession
from app import engine

# Create a synchronous engine for schema autoload
sync_engine = create_engine('postgresql+psycopg2://qlikuser:qlikpassword@postgres:5432/qlikdb')

metadata = MetaData()

# Define the table
qlik_apps_table = Table('qlik_apps', metadata, autoload_with=sync_engine)

# Define the class
class QlikApps:
    pass

# Create a registry
mapper_registry = registry()

# Map the class to the table
mapper_registry.map_imperatively(QlikApps, qlik_apps_table, primary_key=[qlik_apps_table.c.id])

router = APIRouter()

# Async session local
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

from datetime import datetime, date
from typing import Optional

@router.get("/fetch_apps", response_description="Fetchs Qlik apps from the db, can be filtered.")
async def fetch_apps(
    db: AsyncSession = Depends(get_db),
    owner_name: Optional[str] = None,
    app_name: Optional[str] = None,
    space_type: Optional[str] = None,
    created_at: Optional[date] = None,
    last_reload_time: Optional[date] = None,
    publish_time: Optional[date] = None,
    app_id: Optional[str] = None,
    space_name: Optional[str] = None,
    tenant_id: Optional[str] = None,
    updated_at: Optional[date] = None,
    reload_status: Optional[str] = None
):
    """
    Fetches Qlik apps from the database with optional filters.
    Params:
        owner_name (str, optional): Owner's name.
        app_name (str, optional): App's name.
        space_type (str, optional): Type of space.
        created_at (date, optional): Creation date (YYYY-MM-DD).
        last_reload_time (date, optional): Last reload time (YYYY-MM-DD).
        publish_time (date, optional): Publish time (YYYY-MM-DD).
        app_id (str, optional): App ID.
        space_name (str, optional): Space name.
        tenant_id (str, optional): Tenant ID.
        updated_at (date, optional): Last update date (YYYY-MM-DD).
        reload_status (str, optional): Reload status (ok/error).
    Returns:
        list: List of apps with metadata. Each app is a dictionary in the list.
    """

    # Start with a query that selects everything
    query = select(QlikApps)

    # Build a list of filter conditions
    filters = []

    if owner_name is not None:
        filters.append(QlikApps.owner_name == owner_name)

    if app_name is not None:
        filters.append(QlikApps.app_name == app_name)

    # Add more filters as needed
    if space_type is not None:
        filters.append(QlikApps.space_type == space_type)

    if created_at is not None:
        filters.append(func.date(QlikApps.createdAt) >= created_at)

    if last_reload_time is not None:
        filters.append(func.date(QlikApps.last_reload_time) >= last_reload_time)

    if publish_time is not None:
        filters.append(func.date(QlikApps.publish_time) >= publish_time)

    if updated_at is not None:
        filters.append(func.date(QlikApps.updatedAt) >= updated_at)

    if app_id is not None:
        filters.append(QlikApps.app_id == app_id)

    if space_name is not None:
        filters.append(QlikApps.space_name == space_name)

    if tenant_id is not None:
        filters.append(QlikApps.tenantId == tenant_id)

    if reload_status is not None:
        filters.append(QlikApps.reload_status == reload_status)

    # If any filters were provided, add them to the query
    if filters:
        query = query.where(and_(*filters))

    result = await db.execute(query)
    apps = [row.__dict__ for row in result.scalars()]
    return apps