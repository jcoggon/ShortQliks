from fastapi import APIRouter, Request, HTTPException, Form, Depends
from sqlalchemy.orm import Session
from app.models.qlik_app import QlikApp
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

@app.route('/fetch_and_store_apps', methods=['GET', 'POST'])
def fetch_and_store_apps():
    if requests.method == 'POST':
        tenant_id = Form('tenant_id')
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return ({"message": "Tenant not found"}), 404

        headers = {
            'Authorization': f'Bearer {tenant.qlik_cloud_api_key}',
            'Content-Type': 'application/json'
        }

        hostname = tenant.hostnames.split(',')[-1]
        next_url = f"https://{hostname}/api/v1/apps"
        while next_url:
            response = requests.get(next_url, headers=headers)
            if response.status_code != 200:
                return ({"error": "Failed to fetch data from Qlik Cloud", "response": response.text}), 500

            response_data = response.json()
            apps = response_data.get('data', [])
            for app_data in apps:
                attributes = app_data.get('attributes', {})
                app = create_app_from_data(attributes)
                app.tenant_id = tenant.id  # Set the tenant_id field to the ID of the tenant
                db.session.merge(app)
            db.commit()

            next_link = response_data.get('links', {}).get('next')
            next_url = next_link.get('href') if next_link else None

    return ({"message": "Apps fetched and stored successfully!"}), 200

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