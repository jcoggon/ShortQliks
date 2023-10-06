from fastapi import Request, HTTPException, Form, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.tenant import Tenant
from app import SessionLocal
from app.main.routes import router

@router.post('/create_tenant')
async def create_tenant(
    qlik_cloud_url: str = Form(...),
    qlik_cloud_api_key: str = Form(...),
    user_id: int = Form(...),
    db: Session = Depends(SessionLocal)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    headers = {
        'Authorization': f'Bearer {qlik_cloud_api_key}',
        'Content-Type': 'application/json'
    }

    response = Request.get(f"https://{qlik_cloud_url}/api/v1/tenants", headers=headers)
    response_data = response.json()
    tenants = response_data.get('data', [])

    for tenant_data in tenants:
        tenant_data['qlik_cloud_api_key'] = qlik_cloud_api_key
        tenant = create_tenant_from_data(tenant_data, db)
        # Check if the association already exists
        if tenant not in user.tenants:
            user.tenants.append(tenant)  # Add the tenant to the user's tenants

    db.commit()
    tenant_id = tenant.id

    if response.status_code == 200:
        return {"status": 200, "message": "Tenant created successfully", "tenant_id": tenant_id}

    return {"status": response.status_code, "message": "API call was not successful"}

def create_tenant_from_data(tenant_data, db):
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
