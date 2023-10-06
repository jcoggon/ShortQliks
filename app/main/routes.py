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

router = APIRouter()
