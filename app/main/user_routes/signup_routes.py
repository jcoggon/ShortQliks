from fastapi import APIRouter, Request, HTTPException, Form, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.tenant import Tenant
from app.models.associations import user_tenants
from app.main.qlik_routes.fetch_and_store_apps_routes import fetch_and_store_apps
from app.main.qlik_routes.fetch_and_store_reload_tasks_routes import fetch_and_store_reload_tasks
from app.main.qlik_routes.fetch_and_store_users_routes import fetch_and_store_users
from app.main.qlik_routes.fetch_and_store_spaces_routes import fetch_and_store_spaces
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from config import Config
from app import SessionLocal
from app.main.logging_config import logger
from app.main.routes import router


@router.post('/signup')
async def signup(
    _id: str = Form(...),
    fullname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    qlik_cloud_tenant_url: str = Form(...),
    qlik_cloud_api_key: str = Form(...)
):
    db = SessionLocal()
    try:
        user = create_user_from_data(db, _id, fullname, email, password, qlik_cloud_tenant_url)
        qlik_cloud_api_key = qlik_cloud_api_key  # Not sure if this line is needed

        # Add the user to the session and commit to get the user.id
        db.add(user)
        db.commit()

        # Validate the provided tenant URL and Qlik Cloud API key
        if not check_tenant(db, user, qlik_cloud_api_key):
            return {"message": "Invalid tenant URL or Qlik Cloud API key. Please try again."}

        # Generate the API key
        s = Serializer(Config['SECRET_KEY'], '1800')
        user.admin_dashboard_api_key = s.dumps({'user_id': user.id})

        # Fetch and store data for each tenant
        tenants = user.tenants
        for tenant in tenants:
            fetch_and_store_apps(tenant.id)
            fetch_and_store_users(tenant.id)
            fetch_and_store_reload_tasks(tenant.id)
            fetch_and_store_spaces(tenant.id)

        # Commit the user again to save the admin_dashboard_api_key
        db.commit()

        return {"message": "Signup successful."}
    except Exception as e:
        logger.error(str(e))
        return {"message": "Signup failed."}
    finally:
        db.close()

def check_tenant(db, user, qlik_cloud_api_key):
    headers = {
        'Authorization': f'Bearer {qlik_cloud_api_key}',
        'Content-Type': 'application/json'
    }
    response = Request.get(f"https://{user.qlik_cloud_tenant_url}/api/v1/tenants", headers=headers)
    response_data = response.json()
    tenants = response_data.get('data', [])
    for tenant_data in tenants:
        tenant_data['qlik_cloud_api_key'] = qlik_cloud_api_key
        tenant = create_tenant_from_data(db, tenant_data)
        # Check if the association already exists
        if tenant not in user.tenants:
            user.tenants.append(tenant)  # Add the tenant to the user's tenants
    db.commit()
    return response.status_code == 200  # Return True if the API call was successful, False otherwise

def create_user_from_data(db, _id, fullname, email, password, qlik_cloud_tenant_url):
    return User(
        _id=_id,
        fullname=fullname,
        email=email,
        password=password,
        qlik_cloud_tenant_url=qlik_cloud_tenant_url
    )
    
def create_tenant_from_data(db, tenant_data):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_data.get('id')).first()
    if tenant is None:
        tenant = Tenant(
            id=tenant_data.get('id'),
            name=tenant_data.get('name'),
            hostnames=','.join(tenant_data.get('hostnames', [])),
            createdByUser=tenant_data.get('createdByUser'),
            datacenter=tenant_data.get('datacenter'),
            created=tenant_data.get('created'),
            lastUpdated=tenant_data.get('lastUpdated'),
            status=tenant_data.get('status'),
            autoAssignCreateSharedSpacesRoleToProfessionals=tenant_data.get('autoAssignCreateSharedSpacesRoleToProfessionals'),
            autoAssignPrivateAnalyticsContentCreatorRoleToProfessionals=tenant_data.get('autoAssignPrivateAnalyticsContentCreatorRoleToProfessionals'),
            autoAssignDataServicesContributorRoleToProfessionals=tenant_data.get('autoAssignDataServicesContributorRoleToProfessionals'),
            enableAnalyticCreation=tenant_data.get('enableAnalyticCreation'),
            qlik_cloud_api_key=tenant_data.get('qlik_cloud_api_key')
        )
    else:
        tenant.name = tenant_data.get('name')
        tenant.hostnames = ','.join(tenant_data.get('hostnames', []))
        tenant.createdByUser = tenant_data.get('createdByUser')
        tenant.datacenter = tenant_data.get('datacenter')
        tenant.created = tenant_data.get('created')
        tenant.lastUpdated = tenant_data.get('lastUpdated')
        tenant.status = tenant_data.get('status')
        tenant.autoAssignCreateSharedSpacesRoleToProfessionals = tenant_data.get('autoAssignCreateSharedSpacesRoleToProfessionals')
        tenant.autoAssignPrivateAnalyticsContentCreatorRoleToProfessionals = tenant_data.get('autoAssignPrivateAnalyticsContentCreatorRoleToProfessionals')
        tenant.autoAssignDataServicesContributorRoleToProfessionals = tenant_data.get('autoAssignDataServicesContributorRoleToProfessionals')
        tenant.enableAnalyticCreation = tenant_data.get('enableAnalyticCreation')
        tenant.qlik_cloud_api_key = tenant_data.get('qlik_cloud_api_key')
    return tenant
