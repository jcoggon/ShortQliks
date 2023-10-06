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

@app.route('/onboard', methods=['GET', 'POST'])
def onboard():
    if requests.method == 'POST':
        app_name = 'ShortQliks'
        
        budibase_api_key = 'budibase'
        headers = {
            'x-budibase-api-key': f'{budibase_api_key}',
            'Content-Type': 'application/json'
        }
        email = Form('email')
        firstName = Form('firstName')
        lastName = Form('lastName')
        
        response = requests.post('http://web:5000/app_search/{app_name}'.format(app_name=app_name))
        if response.status_code == 200:
            response_data = response.json()
            app_id = response_data.get('_id')
        else:
            # # flash('Failed to find app.')
        
            data = [{"email": email,"userInfo":{"apps":{ app_id:"BASIC" }}}]
            response = requests.post(f"http://bbproxy:10000/api/global/users/onboard", headers=headers, json=data)
            response_data = response.json()
            users = response_data.get('successful', [])
            password = users[0]['password']
            for user_data in users:
                user = create_user_onboarding(user_data)
                # Add the user to the session and commit to get the user.id
                db.add(user)
                db.commit()
                
                update_data = {"firstName": firstName, "lastName": lastName, "forceResetPassword": False, "roles":{ app_id:"BASIC" }}
                response = requests.put('http://bbproxy:10000/api/public/v1/users/{_id}'.format(_id=user_data['_id']), headers=headers, json=update_data)
                # response_update = response.json()
                if response.status_code == 200:
                    print('Updated user.')
                else:
                    print('Failed to update user.')
                
                return ({"user_id": user.id, "password": password}), 200
            else:
                # # flash('Onboarding Failed')
                return ({"onboarding": 'Failed'}), 404
            
def create_user_onboarding(data):
    return User(
        _id=data['_id'],
        email=data['email'],
        password=data['password']
    )