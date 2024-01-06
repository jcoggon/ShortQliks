from fastapi import APIRouter, HTTPException, Body, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.reload_task import ReloadTask
from app.models.tenant import Tenant
from app import engine  # Ensure this is your async-compatible engine
import httpx
from dateutil.parser import parse
from datetime import timezone

router = APIRouter()

# Async session local
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class TenantId(BaseModel):
    tenant_id: str = Field(..., description="The ID of the tenant.")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post('/fetch_and_store_reload_tasks', response_description="The status of fetching and storing reload tasks.")
async def fetch_and_store_reload_tasks(tenant_id: TenantId = Body(...), db: AsyncSession = Depends(get_db)):
    """
    Fetches Qlik reload tasks for a tenant and stores them in the database.
    Takes a tenant ID, fetches reload tasks via Qlik Cloud API, and stores them. 
    If tenant ID is not found, an HTTPException is raised.
    Args:
        tenant_id (TenantId): A model with a 'tenant_id' field.
    Returns:
        dict: Status of the operation.
    """
    tenant_id_str = tenant_id.tenant_id  # Extract the tenant_id string
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id_str))
    tenant = result.scalars().first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    headers = {
        'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
        'Content-Type': 'application/json'
    }

    hostname = tenant.hostnames.split(',')[-1]
    next_url = f"https://{hostname}/api/v1/reload-tasks"

    async with httpx.AsyncClient() as client:
        while next_url:
            response = await client.get(next_url, headers=headers)
            if response.status_code != 200:
                return {"error": "Failed to fetch data from Qlik Cloud", "response": response.text}

            response_data = response.json()
            tasks = response_data.get('data', [])
            for task_data in tasks:
                task_id = task_data.get('id')
                result = await db.execute(select(ReloadTask).where(ReloadTask.id == task_id))
                existing_task = result.scalars().first()
                if existing_task:
                    # Update the existing task's attributes
                    for key, value in task_data.items():
                        if key in ['startDateTime', 'lastExecutionTime', 'nextExecutionTime']:
                            value = parse(value).astimezone(timezone.utc).replace(tzinfo=None) if value else None
                        elif key == 'recurrence' and isinstance(value, list):
                            value = ', '.join(value)
                        setattr(existing_task, key, value)
                    existing_task.tenant_id = tenant.id
                else:
                    # Create a new task
                    existing_task = create_reload_task_from_data(task_data)
                    existing_task.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
                    db.add(existing_task)

                await db.commit()  # Commit the session after adding or updating the task

            next_link = response_data.get('links', {}).get('next', {})
            next_url = next_link.get('href') if next_link else None

    return {"message": "Reload tasks fetched and stored successfully!"}

def create_reload_task_from_data(attributes):
    recurrence = attributes.get('recurrence')
    if isinstance(recurrence, list):
        recurrence = ';'.join(recurrence)
    return ReloadTask(
        id=attributes.get('id'),
        appId=attributes.get('appId'),
        partial=attributes.get('partial'),
        timeZone=attributes.get('timeZone'),
        autoReload=attributes.get('autoReload'),
        recurrence=recurrence,
        endDateTime=parse(attributes.get('endDateTime')).astimezone(timezone.utc).replace(tzinfo=None) if attributes.get('endDateTime') else None,
        startDateTime=parse(attributes.get('startDateTime')).astimezone(timezone.utc).replace(tzinfo=None) if attributes.get('startDateTime') else None,
        autoReloadPartial=attributes.get('autoReloadPartial'),
        log=attributes.get('log'),
        state=attributes.get('state'),
        userId=attributes.get('userId'),
        spaceId=attributes.get('spaceId'),
        tenantId=attributes.get('tenantId'),
        fortressId=attributes.get('fortressId'),
        lastExecutionTime=parse(attributes.get('lastExecutionTime')).astimezone(timezone.utc).replace(tzinfo=None) if attributes.get('lastExecutionTime') else None,
        nextExecutionTime=parse(attributes.get('nextExecutionTime')).astimezone(timezone.utc).replace(tzinfo=None) if attributes.get('nextExecutionTime') else None,
        tenant_id=attributes.get('tenant_id')
    )