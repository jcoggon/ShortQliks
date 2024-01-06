from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.qlik_user import QlikUser, AssignedGroup, AssignedRole, user_group_association, user_role_association
from app.models.tenant import Tenant
from app import engine  # Ensure this is your async-compatible engine
import httpx
from datetime import datetime
from sqlalchemy import insert
from sqlalchemy.orm import selectinload

router = APIRouter()

# Async session local
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class TenantId(BaseModel):
    tenant_id: str = Field(..., description="The ID of the tenant.")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/fetch_and_store_users", response_description="The status of fetching and storing users.")
async def fetch_and_store_users(tenant_id: TenantId = Body(...), db: AsyncSession = Depends(get_db)):
    """
    Fetches Qlik users for a tenant and stores them in the database.
    Takes a tenant ID, fetches users via Qlik Cloud API, and stores them. 
    If tenant ID is not found, an HTTPException is raised.
    Args:
        tenant_id (TenantId): A model with a 'tenant_id' field.
    Returns:
        dict: Status of the operation.
    """
    tenant_id_str = tenant_id.tenant_id  # Extract the tenant_id string
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id_str))
    tenant = result.scalars().first()  # Fetch the tenant from the result
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    headers = {
        'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
        'Content-Type': 'application/json'
    }

    hostname = tenant.hostnames.split(',')[-1]
    next_url = f"https://{hostname}/api/v1/users"

    async with httpx.AsyncClient() as client:
        while next_url:
            response = await client.get(next_url, headers=headers)
            if response.status_code != 200:
                return {"error": "Failed to fetch data from Qlik Cloud", "response": response.text}

            response_data = response.json()
            users = response_data.get('data', [])
            for user_data in users:
                user_id = user_data.get('id')
                qlik_app_link = user_data.get('links', {}).get('self', {}).get('href')
                attributes = {
                    'name': user_data.get('name'),
                    'email': user_data.get('email', 'N/A'),
                    'tenantId': user_data.get('tenantId'),
                    'status': user_data.get('status'),
                    'created': datetime.fromisoformat(user_data.get('created').replace('Z', '')),
                    'lastUpdated': datetime.fromisoformat(user_data.get('lastUpdated').replace('Z', '')),
                    'qlik_app_link': qlik_app_link
                }

                # Check if user already exists
                result = await db.execute(
                    select(QlikUser)
                    .options(selectinload(QlikUser.groups), selectinload(QlikUser.roles))
                    .where(QlikUser.id == user_id)
                )
                existing_user = result.scalars().first()

                if existing_user:
                    # Update the existing user's attributes
                    for key, value in attributes.items():
                        setattr(existing_user, key, value)
                else:
                    # Create a new user
                    existing_user = QlikUser(id=user_id, **attributes)
                    db.add(existing_user)

                # Manage user groups
                for group_data in user_data.get('assignedGroups', []):
                    result = await db.execute(select(AssignedGroup).where(AssignedGroup.id == group_data['id']))
                    group = result.scalars().first()
                    if group:
                        # Update the existing group's attributes
                        group.name = group_data['name']
                    else:
                        # Create a new group
                        group = AssignedGroup(
                            id=group_data['id'],
                            name=group_data['name']
                        )
                        db.add(group)
                    await db.commit()  # Commit the session after adding or updating the group

                    # Add group to user
                    await db.execute(
                        insert(user_group_association)
                        .values(user_id=user_id, group_id=group.id)
                    )

                # Manage user roles
                for role_data in user_data.get('assignedRoles', []):
                    result = await db.execute(select(AssignedRole).where(AssignedRole.id == role_data['id']))
                    role = result.scalars().first()
                    if role:
                        # Update the existing role's attributes
                        role.name = role_data['name']
                        role.type = role_data['type']
                        role.level = role_data['level']
                        role.permissions = ",".join(role_data.get('permissions', []))
                    else:
                        # Create a new role
                        role = AssignedRole(
                            id=role_data['id'],
                            name=role_data['name'],
                            type=role_data['type'],
                            level=role_data['level'],
                            permissions=",".join(role_data.get('permissions', []))
                        )
                        db.add(role)
                    await db.commit()  # Commit the session after adding or updating the role

                    # Add role to user
                    await db.execute(
                        insert(user_role_association)
                        .values(user_id=user_id, role_id=role.id)
                    )

                await db.commit()

            next_link = response_data.get('links', {}).get('next')
            next_url = next_link.get('href') if next_link else None

    return {"message": "Users fetched and stored successfully!"}

def create_qlik_user_from_data(user_id, attributes, qlik_app_link):
    return QlikUser(
        id=user_id,
        name=attributes.get('name'),
        email=attributes.get('email', 'N/A'),  # Default to 'N/A' if email is missing
        tenantId=attributes.get('tenantId'),
        status=attributes.get('status'),
        created=attributes.get('created'),
        lastUpdated=attributes.get('lastUpdated'),
        qlik_app_link=qlik_app_link
    )