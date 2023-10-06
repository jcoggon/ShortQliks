from sqlalchemy import Column, String, DateTime, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel

Base = declarative_base()

# SQLAlchemy models for database interaction
class QlikUser(Base):
    __tablename__ = 'qlik_user'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String, default='N/A')
    tenantId = Column(String)
    status = Column(String)
    created = Column(DateTime)
    lastUpdated = Column(DateTime)
    qlik_app_link = Column(String)

class AssignedGroup(Base):
    __tablename__ = 'assigned_group'
    
    id = Column(String, primary_key=True)
    name = Column(String)

class AssignedRole(Base):
    __tablename__ = 'assigned_role'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    type = Column(String)
    level = Column(String)
    permissions = Column(String)  # Assuming permissions are stored as comma-separated values

# Association tables
user_group_association = Table('user_group_association',
                               Base.metadata,
                               Column('user_id', String, ForeignKey('qlik_user.id')),
                               Column('group_id', String, ForeignKey('assigned_group.id'))
                               )

user_role_association = Table('user_role_association',
                              Base.metadata,
                              Column('user_id', String, ForeignKey('qlik_user.id')),
                              Column('role_id', String, ForeignKey('assigned_role.id'))
                              )

# Relationships
QlikUser.groups = relationship('AssignedGroup', secondary=user_group_association, back_populates='users')
QlikUser.roles = relationship('AssignedRole', secondary=user_role_association, back_populates='users')

# Pydantic models for request and response
class QlikUserCreate(BaseModel):
    name: str
    email: str
    tenantId: str
    status: str

class QlikUserResponse(QlikUserCreate):
    id: str
    created: str
    lastUpdated: str
    qlik_app_link: str
