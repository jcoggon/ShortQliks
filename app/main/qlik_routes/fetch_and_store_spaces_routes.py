from fastapi import Request, HTTPException, Form, Depends
from sqlalchemy.orm import Session
from app.models.tenant import Tenant
from app.models.associations import user_tenants
from app.models.qlik_space import QlikSpace
from app import SessionLocal
from app.main.logging_config import logger
from app.main.routes import router

@router.post('/fetch_and_store_spaces')
async def fetch_and_store_spaces(tenant_id: int = Form(...), db: Session = Depends(SessionLocal)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    headers = {
        'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
    }

    hostname = tenant.hostnames.split(',')[-1]
    next_url = f"https://{hostname}/api/v1/spaces"

    while next_url:
        response = Request.get(next_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed API call with status {response.status_code}: {response.text}")
            return {"error": "Failed to fetch data from Qlik Cloud", "response": response.text}

        try:
            response_data = response.json()
            spaces = response_data.get('data', [])
            if not spaces:
                print("No spaces found in the API response.")
                return {"error": "No spaces found in the response from Qlik Cloud API"}

            for space_data in spaces:
                space_id = space_data.get('id')
                existing_space = db.query(QlikSpace).filter(QlikSpace.id == space_id).first()
                if not existing_space:
                    space = create_space_from_data(space_data)
                    db.add(space)
                    existing_space = space
                    existing_space.tenant_id = tenant.id
                db.commit()

            next_link = response_data.get('links', {}).get('next', {})
            next_url = next_link.get('href') if next_link else None

        except Exception as e:
            print(f"Exception encountered: {str(e)}")
            return {"error": str(e)}

    return {"message": "Spaces fetched and stored successfully!"}

def create_space_from_data(attributes):
    return QlikSpace(
        id=attributes.get('id'),
        name=attributes.get('name'),
        type=attributes.get('type'),
        owner_id=attributes.get('ownerId'),
        tenant_id=attributes.get('tenantId'),
        created_at=attributes.get('createdAt'),
        updated_at=attributes.get('updatedAt'),
        description=attributes.get('description'),
        meta=attributes.get('meta'),
        links=attributes.get('links')
    )
