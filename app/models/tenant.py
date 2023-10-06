from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

# Assuming user_tenants association table is already defined

# SQLAlchemy model for database interaction
class Tenant(Base):
    __tablename__ = 'tenant'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    hostnames = Column(String)
    createdByUser = Column(String)
    datacenter = Column(String)
    created = Column(String)
    lastUpdated = Column(String)
    status = Column(String)
    autoAssignCreateSharedSpacesRoleToProfessionals = Column(Boolean)
    autoAssignPrivateAnalyticsContentCreatorRoleToProfessionals = Column(Boolean)
    autoAssignDataServicesContributorRoleToProfessionals = Column(Boolean)
    enableAnalyticCreation = Column(Boolean)
    qlik_cloud_api_key = Column(String)
    users = relationship('User', secondary='user_tenants')  # Assuming the table name as a string

# Pydantic models for request and response
class TenantCreate(BaseModel):
    name: str
    hostnames: str
    createdByUser: str
    datacenter: str
    created: str
    lastUpdated: str
    status: str
    autoAssignCreateSharedSpacesRoleToProfessionals: bool
    autoAssignPrivateAnalyticsContentCreatorRoleToProfessionals: bool
    autoAssignDataServicesContributorRoleToProfessionals: bool
    enableAnalyticCreation: bool
    qlik_cloud_api_key: str

class TenantResponse(TenantCreate):
    id: str
