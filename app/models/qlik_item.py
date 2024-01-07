from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from app import Base

# SQLAlchemy model for database interaction
class QlikItem(Base):
    __tablename__ = 'qlik_item'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    ownerId = Column(String)
    spaceId = Column(String)
    tenantId = Column(String)
    createdAt = Column(String)
    creatorId = Column(String)
    updatedAt = Column(String)
    updaterId = Column(String)
    resourceId = Column(String)
    description = Column(String)
    isFavorited = Column(Boolean)
    thumbnailId = Column(String)
    resourceLink = Column(String)
    resourceSize = Column(JSON)
    resourceType = Column(String)
    resourceSubType = Column(String)
    resourceCreatedAt = Column(String)
    resourceUpdatedAt = Column(String)
    resourceAttributes = Column(JSON)
    resourceReloadStatus = Column(String)
    resourceReloadEndTime = Column(String)
    resourceCustomAttributes = Column(JSON)
    meta = Column(JSON)
    links = Column(JSON)
    itemViews = Column(JSON)

# Pydantic models for request and response
class QlikItemCreate(BaseModel):
    name: str
    ownerId: str
    spaceId: str
    tenantId: str
    createdAt: str
    creatorId: str
    updatedAt: str
    updaterId: str
    resourceId: str
    description: str
    isFavorited: bool
    thumbnailId: str
    resourceLink: str
    resourceSize: dict
    resourceType: str
    resourceSubType: str
    resourceCreatedAt: str
    resourceUpdatedAt: str
    resourceAttributes: dict
    resourceReloadStatus: str
    resourceReloadEndTime: str
    resourceCustomAttributes: dict
    meta: dict
    links: dict
    itemViews: dict

class QlikItemResponse(QlikItemCreate):
    id: str