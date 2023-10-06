from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from passlib.context import CryptContext

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Assuming user_tenants association table is already defined

# SQLAlchemy model for database interaction
class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    _id = Column(String)
    fullname = Column(String)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String)
    qlik_cloud_tenant_url = Column(String)
    admin_dashboard_api_key = Column(String, unique=True)
    tenants = relationship('Tenant', secondary='user_tenants')  # Assuming the table name as a string

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = pwd_context.hash(password)

    def check_password(self, password):
        return pwd_context.verify(password, self.password_hash)

# Pydantic models for request and response
class UserCreate(BaseModel):
    _id: str
    fullname: str
    email: str
    password: str
    qlik_cloud_tenant_url: str
    admin_dashboard_api_key: str

class UserResponse(UserCreate):
    id: int
