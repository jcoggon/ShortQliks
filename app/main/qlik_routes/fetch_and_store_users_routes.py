from fastapi import Form, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.models.qlik_user import QlikUser, AssignedGroup, AssignedRole
from app.models.user import User
from app.models.tenant import Tenant
from app import app
from config import Config
from app import SessionLocal
from app.main.logging_config import logger
from app.main.routes import router


@router.post('/fetch_and_store_users')
async def fetch_and_store_users(
    tenant_id: int = Form(...),
    db: Session = Depends(SessionLocal)
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    headers = {
        'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
        'Content-Type': 'application/json'
    }

    hostname = tenant.hostnames.split(',')[-1]
    next_url = f"https://{hostname}/api/v1/users"
    try:
        while next_url:
            response = Request.get(next_url, headers=headers)
            if response.status_code != 200:
                print(f"Failed API call with status {response.status_code}: {response.text}")
                return {"error": "Failed to fetch data from Qlik Cloud", "response": response.text}

            try:
                response_data = response.json()
                users = response_data.get('data', [])
                if not users:
                    print("No users found in the API response.")
                    return {"error": "No users found in the response from Qlik Cloud API"}

                for user_data in users:
                    user_id = user_data.get('id')
                    qlik_app_link = user_data.get('links', {}).get('self', {}).get('href')
                    attributes = {
                        'name': user_data.get('name'),
                        'email': user_data.get('email', 'N/A'),
                        'tenantId': user_data.get('tenantId'),
                        'status': user_data.get('status'),
                        'created': user_data.get('created'),
                        'lastUpdated': user_data.get('lastUpdated'),
                        'qlik_app_link': qlik_app_link
                    }

                    # Check if user already exists
                    existing_user = db.query(QlikUser).filter(QlikUser.id == user_id).first()
                    if not existing_user:
                        existing_user = QlikUser(id=user_id)
                        db.add(existing_user)

                    # Update the existing user's attributes
                    for key, value in attributes.items():
                        setattr(existing_user, key, value)

                    # Manage user groups
                    for group_data in user_data.get('assignedGroups', []):
                        group = db.query(AssignedGroup).filter(AssignedGroup.id == group_data['id']).first() or AssignedGroup(
                            id=group_data['id'],
                            name=group_data['name']
                        )
                        existing_user.groups.append(group)
                        db.merge(group)

                    # Manage user roles
                    for role_data in user_data.get('assignedRoles', []):
                        role = db.query(AssignedRole).filter(AssignedRole.id == role_data['id']).first() or AssignedRole(
                            id=role_data['id'],
                            name=role_data['name'],
                            type=role_data['type'],
                            level=role_data['level'],
                            permissions=",".join(role_data.get('permissions', []))
                        )
                        existing_user.roles.append(role)
                        db.merge(role)

                # Check if there's a next page to fetch
                next_link = response_data.get('links', {}).get('next')
                next_url = next_link.get('href') if next_link else None

            except Exception as e:
                print(f"Exception encountered: {str(e)}")
                return {"error": str(e)}

        db.commit()
    finally:
        # Always close the session to return it to the pool
        db.close()

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