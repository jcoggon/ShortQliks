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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if requests.method == 'POST':
        data = Form
        user = User.query.filter_by(email=Form('email')).first()
        if user and user.check_password(Form('password')):
            # # flash('Login successful.')
            return ({"user_id": user.id}), 200 #render_template('login.html')
        else:
            # # flash('Invalid email or password.')
            return ({"login": 'Failed'}), 404 #render_template('login.html')