from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

# SQLAlchemy model for database interaction
class QlikApp(Base):
    __tablename__ = 'qlik_app'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    owner = Column(String)
    usage = Column(String)
    ownerId = Column(String)
    encrypted = Column(Boolean)
    published = Column(Boolean)
    thumbnail = Column(String)
    createdDate = Column(String)
    description = Column(Text)
    originAppId = Column(String)
    publishTime = Column(String)
    dynamicColor = Column(String)
    modifiedDate = Column(String)
    lastReloadTime = Column(String)
    hasSectionAccess = Column(Boolean)
    isDirectQueryMode = Column(Boolean)
    tenant_id = Column(String, ForeignKey('tenant.id'))

# Pydantic models for request and response
class QlikAppCreate(BaseModel):
    name: str
    owner: str
    usage: str
    ownerId: str
    encrypted: bool
    published: bool
    thumbnail: str
    createdDate: str
    description: str
    originAppId: str
    publishTime: str
    dynamicColor: str
    modifiedDate: str
    lastReloadTime: str
    hasSectionAccess: bool
    isDirectQueryMode: bool
    tenant_id: str

class QlikAppResponse(QlikAppCreate):
    id: str
