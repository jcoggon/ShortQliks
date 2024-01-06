from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.qlik_space import QlikSpace  # Ensure correct import
from app.models.tenant import Tenant
from app import engine  # Ensure this is your async-compatible engine
import httpx

router = APIRouter()

# Async session local
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class TenantId(BaseModel):
    tenant_id: str = Field(..., description="The ID of the tenant.")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/fetch_and_store_spaces", response_description="The status of fetching and storing spaces.")
async def fetch_and_store_spaces(tenant_id: TenantId = Body(...), db: AsyncSession = Depends(get_db)):
    """
    Fetches Qlik spaces for a tenant and stores them in the database.
    Takes a tenant ID, fetches spaces via Qlik Cloud API, and stores them. 
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
    }

    hostname = tenant.hostnames.split(',')[-1]
    next_url = f"https://{hostname}/api/v1/spaces"

    async with httpx.AsyncClient() as client:
        while next_url:
            response = await client.get(next_url, headers=headers)
            if response.status_code != 200:
                return {"error": "Failed to fetch data from Qlik Cloud", "response": response.text}

            response_data = response.json()
            spaces = response_data.get('data', [])
            for space_data in spaces:
                result = await db.execute(select(QlikSpace).where(QlikSpace.id == space_data['id']))
                space = result.scalars().first()
                if space:
                    # Update the existing space's attributes
                    space.name = space_data.get('name')
                    space.type = space_data.get('type')
                    space.owner_id = space_data.get('ownerId')
                    space.tenant_id = space_data.get('tenantId')
                    space.created_at = parse(space_data.get('createdAt')).astimezone(timezone.utc).replace(tzinfo=None) if space_data.get('createdAt') else None
                    space.updated_at = parse(space_data.get('updatedAt')).astimezone(timezone.utc).replace(tzinfo=None) if space_data.get('updatedAt') else None
                    space.description = space_data.get('description')
                    space.meta = space_data.get('meta')
                    space.links = space_data.get('links')
                else:
                    # Create a new space
                    space = create_space_from_data(space_data['id'], space_data)
                    space.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
                    db.add(space)
                await db.commit()  # Commit the session after adding or updating the space

            next_link = response_data.get('links', {}).get('next')
            next_url = next_link.get('href') if next_link else None

    return {"message": "Spaces fetched and stored successfully!"}

from dateutil.parser import parse
from datetime import timezone

def create_space_from_data(id, space_data):
    created_at = parse(space_data.get('createdAt')) if space_data.get('createdAt') else None
    updated_at = parse(space_data.get('updatedAt')) if space_data.get('updatedAt') else None
    if created_at and created_at.tzinfo:
        created_at = created_at.astimezone(timezone.utc).replace(tzinfo=None)
    if updated_at and updated_at.tzinfo:
        updated_at = updated_at.astimezone(timezone.utc).replace(tzinfo=None)
    return QlikSpace(
        id=id,  # Use the passed id
        name=space_data.get('name'),
        type=space_data.get('type'),
        owner_id=space_data.get('ownerId'),
        tenant_id=space_data.get('tenantId'),
        created_at=created_at,
        updated_at=updated_at,
        description=space_data.get('description'),
        meta=space_data.get('meta'),
        links=space_data.get('links')
    )