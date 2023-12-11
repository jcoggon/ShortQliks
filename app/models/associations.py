from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app import Base
# Base = declarative_base()

# SQLAlchemy models for database interaction
# class User(Base):
#     __tablename__ = 'user'
#     __table_args__ = {'extend_existing': True}
    
#     id = Column(Integer, primary_key=True)
#     _id = Column(String)
#     fullname = Column(String)
#     email = Column(String, unique=True, nullable=False)
#     password_hash = Column(String)
#     qlik_cloud_tenant_url = Column(String)
#     admin_dashboard_api_key = Column(String, unique=True)
#     tenants = relationship('Tenant', secondary='user_tenants')  # Assuming the table name as a string

# class Tenant(Base):
#     __tablename__ = 'tenant'
#     __table_args__ = {'extend_existing': True}
    
#     id = Column(String, primary_key=True)
#     name = Column(String)
#     hostnames = Column(String)
#     createdByUser = Column(String)
#     datacenter = Column(String)
#     created = Column(String)
#     lastUpdated = Column(String)
#     status = Column(String)
#     autoAssignCreateSharedSpacesRoleToProfessionals = Column(Boolean)
#     autoAssignPrivateAnalyticsContentCreatorRoleToProfessionals = Column(Boolean)
#     autoAssignDataServicesContributorRoleToProfessionals = Column(Boolean)
#     enableAnalyticCreation = Column(Boolean)
#     qlik_cloud_api_key = Column(String)
#     users = relationship('User', secondary='user_tenants')  # Assuming the table name as a string

# Association table
user_tenants = Table('user_tenants',
                     Base.metadata,
                     Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
                     Column('tenant_id', String, ForeignKey('tenant.id'), primary_key=True)
                     )
