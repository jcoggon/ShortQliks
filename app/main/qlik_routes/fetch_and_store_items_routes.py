from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.qlik_item import QlikItem  # Ensure correct import
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

@router.post("/fetch_and_store_items", response_description="The status of fetching and storing items.")
async def fetch_and_store_items(tenant_id: TenantId = Body(...), db: AsyncSession = Depends(get_db)):
    """
    Fetches Qlik items for a tenant and stores them in the database.
    Takes a tenant ID, fetches items via Qlik Cloud API, and stores them. 
    If tenant ID is not found, an HTTPException is raised.
    Args:
        tenant_id (TenantId): A model with a 'tenant_id' field.
    Returns:
        dict: Status of the operation.
    """
    tenant_id_str = tenant_id.tenant_id  # Extract the tenant_id string
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id_str))  # Use the tenant_id string
    tenant = result.scalars().first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    headers = {
        'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
        'Content-Type': 'application/json'
    }

    hostname = tenant.hostnames.split(',')[-1]
    next_url = f"https://{hostname}/api/v1/items"  # Change the endpoint to items

    async with httpx.AsyncClient() as client:
        while next_url:
            response = await client.get(next_url, headers=headers, follow_redirects=False)
            
            if response.status_code == 308:
                next_url = response.headers.get('Location')
                print(f"Redirecting to: {next_url}")
                continue

            if response.status_code != 200:
                return {"error": "Failed to fetch data from Qlik Cloud", "response": response.text}

            response_data = response.json()
            items = response_data.get('data', [])
            for item_data in items:
                attributes = item_data  # Change this line
                item_id = attributes.get('id')

                # Check if item already exists
                result = await db.execute(select(QlikItem).where(QlikItem.id == item_id))
                existing_item = result.scalars().first()

                if existing_item:
                    # Update the existing item's attributes
                    for key, value in attributes.items():
                        setattr(existing_item, key, value)
                else:
                    # Create a new item
                    existing_item = create_item_from_data(attributes)
                    existing_item.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
                    db.add(existing_item)

                await db.commit()

            next_link = response_data.get('links', {}).get('next')
            next_url = next_link.get('href') if next_link else None

    return {"message": "Items fetched and stored successfully!"}

def create_item_from_data(attributes):
    return QlikItem(
        id=attributes.get('id'),
        name=attributes.get('name'),
        ownerId=attributes.get('ownerId'),
        spaceId=attributes.get('spaceId'),
        tenantId=attributes.get('tenantId'),
        createdAt=attributes.get('createdAt'),
        creatorId=attributes.get('creatorId'),
        updatedAt=attributes.get('updatedAt'),
        updaterId=attributes.get('updaterId'),
        resourceId=attributes.get('resourceId'),
        description=attributes.get('description'),
        isFavorited=attributes.get('isFavorited'),
        thumbnailId=attributes.get('thumbnailId'),
        resourceLink=attributes.get('resourceLink'),
        resourceSize=attributes.get('resourceSize'),
        resourceType=attributes.get('resourceType'),
        resourceSubType=attributes.get('resourceSubType'),
        resourceCreatedAt=attributes.get('resourceCreatedAt'),
        resourceUpdatedAt=attributes.get('resourceUpdatedAt'),
        resourceAttributes=attributes.get('resourceAttributes'),
        resourceReloadStatus=attributes.get('resourceReloadStatus'),
        resourceReloadEndTime=attributes.get('resourceReloadEndTime'),
        resourceCustomAttributes=attributes.get('resourceCustomAttributes'),
        meta=attributes.get('meta'),
        links=attributes.get('links'),
        itemViews=attributes.get('itemViews')
    )