# app/models/user.py

from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    qlik_cloud_tenant_url = db.Column(db.String(255), nullable=False)
    qlik_cloud_api_key = db.Column(db.String(1000), nullable=True)
    admin_dashboard_api_key = db.Column(db.String(1000), unique=True, nullable=True)

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)