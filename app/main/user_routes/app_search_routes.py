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

@app.route('/app_search/<string:app_name>', methods=['GET', 'POST'])
def app_search(app_name):
    if requests.method == 'POST':
        budibase_api_key = 'budibase'
        headers = {
            'x-budibase-api-key': f'{budibase_api_key}',
            'Content-Type': 'application/json'
        }
        data = {"name": app_name}
        response = requests.post(f"http://bbproxy:10000/api/public/v1/applications/search", headers=headers, json=data)
        response_data = response.json()
        apps = response_data.get('data', [])
        for app_data in apps:
            if app_data['status'] == 'published':
                # # flash('App Found.')
                return ({"_id": app_data['_id']}), 200
        else:
            # # flash('Application not found.')
            return ({"error": 'applicaiton not found'}), 404