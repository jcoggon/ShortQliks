from fastapi import APIRouter, HTTPException, Depends, Form
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

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/fetch_and_store_apps")
async def fetch_and_store_apps(tenant_id: str = Form(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
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
                app = create_app_from_data(attributes)
                app.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
                db.add(app)
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
