from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from app import Base
# Base = declarative_base()

# SQLAlchemy model for database interaction
class QlikSpace(Base):
    __tablename__ = 'qlik_space'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    type = Column(String)
    owner_id = Column(String)
    tenant_id = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    description = Column(Text)
    meta = Column(JSON)
    links = Column(JSON)

# Pydantic models for request and response
class QlikSpaceCreate(BaseModel):
    name: str
    type: str
    owner_id: str
    tenant_id: str
    created_at: str
    updated_at: str
    description: str
    meta: dict
    links: dict

class QlikSpaceResponse(QlikSpaceCreate):
    id: str
