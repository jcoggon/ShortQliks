from fastapi import APIRouter, Request, HTTPException, Form, Depends
from sqlalchemy.orm import Session
from app.models.qlik_app import QlikApp
from app.models.qlik_user import QlikUser, AssignedGroup, AssignedRole
from app.models.reload_task import ReloadTask
from app.models.user import User
from app.models.tenant import Tenant
from app.models.associations import user_tenants
from app.models.qlik_space import QlikSpace
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from app import app
from config import Config
from app import SessionLocal
import requests
from app.main.logging_config import logger
from app.main.routes import router

@app.route('/create_tenant', methods=['GET', 'POST'])
def create_tenant():
    if requests.method == 'POST':
        qlik_cloud_tenant_url = Form('qlik_cloud_url')
        qlik_cloud_api_key = Form('qlik_cloud_api_key')
        user = User.query.filter_by(_id=Form('user_id')).first()
        request_data = Form
        print(request_data)
        headers = {
            'Authorization': f'Bearer {qlik_cloud_api_key}',
            'Content-Type': 'application/json'
        }
        response = requests.get(f"https://{qlik_cloud_tenant_url}/api/v1/tenants", headers=headers)
        response_data = response.json()
        tenants = response_data.get('data', [])
        for tenant_data in tenants:
            tenant_data['qlik_cloud_api_key'] = qlik_cloud_api_key
            tenant = create_tenant_from_data(tenant_data)
            # Check if the association already exists
            if tenant not in user.tenants:
                user.tenants.append(tenant)  # Add the tenant to the user's tenants
        db.commit()
        tenant_id = tenant.id
        if response.status_code == 200:
            return ({"status": 200, "message": "Tenant created successfully", "tenant_id": tenant_id}), 200
        else:
            return ({"status": response.status_code, "message": "API call was not successful"}), response.status_code
    return ({"status": 400, "message": "Invalid request method"}), 400

def create_tenant_from_data(tenant_data):
    tenant = Tenant.query.get(tenant_data.get('id'))
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