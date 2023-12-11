from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app import Base  # Correct import for the base class
from pydantic import BaseModel
from passlib.context import CryptContext
from passlib.hash import sha256_crypt

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# SQLAlchemy model for database interaction
class User(Base):
    __tablename__ = 'user'  # Consider pluralizing table names
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    fullname = Column(String)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String)
    qlik_cloud_tenant_url = Column(String)
    admin_dashboard_api_key = Column(String, unique=True)
    tenants = relationship("Tenant", secondary="user_tenants")  # Ensure 'Tenant' is defined and 'user_tenants' exists

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = sha256_crypt.hash(password)

    def check_password(self, password):
        return sha256_crypt.verify(password, self.password_hash)

# Pydantic models for request and response
class UserCreate(BaseModel):
    user_id: str
    fullname: str
    email: str
    password: str
    qlik_cloud_tenant_url: str
    admin_dashboard_api_key: str

class UserResponse(UserCreate):
    id: int