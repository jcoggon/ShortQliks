from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.qlik_app import QlikApp  # Ensure correct import
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

@router.post("/fetch_and_store_apps", response_description="The status of fetching and storing apps.")
async def fetch_and_store_apps(tenant_id: TenantId = Body(...), db: AsyncSession = Depends(get_db)):
    """
    Fetches Qlik apps for a tenant and stores them in the database.
    Takes a tenant ID, fetches apps via Qlik Cloud API, and stores them. 
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
    next_url = f"https://{hostname}/api/v1/apps"

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
            apps = response_data.get('data', [])
            for app_data in apps:
                attributes = app_data.get('attributes', {})
                app_id = attributes.get('id')

                # Check if app already exists
                result = await db.execute(select(QlikApp).where(QlikApp.id == app_id))
                existing_app = result.scalars().first()

                if existing_app:
                    # Update the existing app's attributes
                    for key, value in attributes.items():
                        setattr(existing_app, key, value)
                else:
                    # Create a new app
                    existing_app = create_app_from_data(attributes)
                    existing_app.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
                    db.add(existing_app)

                await db.commit()

            next_link = response_data.get('links', {}).get('next')
            next_url = next_link.get('href') if next_link else None

    return {"message": "Apps fetched and stored successfully!"}

def create_app_from_data(attributes):
    return QlikApp(
        id=attributes.get('id'),
        name=attributes.get('name'),
        owner=attributes.get('owner'),
        usage=attributes.get('usage'),
        ownerId=attributes.get('ownerId'),
        encrypted=attributes.get('encrypted'),
        published=attributes.get('published'),
        thumbnail=attributes.get('thumbnail'),
        createdDate=attributes.get('createdDate'),
        description=attributes.get('description'),
        originAppId=attributes.get('originAppId'),
        publishTime=attributes.get('publishTime'),
        dynamicColor=attributes.get('dynamicColor'),
        modifiedDate=attributes.get('modifiedDate'),
        lastReloadTime=attributes.get('lastReloadTime'),
        hasSectionAccess=attributes.get('hasSectionAccess'),
        isDirectQueryMode=attributes.get('isDirectQueryMode'),
        tenant_id=attributes.get('tenant_id')
    )
