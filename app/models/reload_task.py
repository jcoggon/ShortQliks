from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

# SQLAlchemy model for database interaction
class ReloadTask(Base):
    __tablename__ = 'reload_task'
    
    id = Column(String, primary_key=True)
    appId = Column(String, nullable=False)
    partial = Column(Boolean, default=False)
    timeZone = Column(String)
    autoReload = Column(Boolean, default=False)
    recurrence = Column(String)  # Use PickleType to store a list, if needed
    endDateTime = Column(DateTime)
    startDateTime = Column(DateTime)
    autoReloadPartial = Column(Boolean, default=False)
    log = Column(Text)
    state = Column(String)
    userId = Column(String, nullable=False)
    spaceId = Column(String)
    tenantId = Column(String)
    fortressId = Column(String)
    lastExecutionTime = Column(DateTime)
    nextExecutionTime = Column(DateTime)
    tenant_id = Column(String, ForeignKey('tenant.id'))

# Pydantic models for request and response
class ReloadTaskCreate(BaseModel):
    appId: str
    partial: bool
    timeZone: str
    autoReload: bool
    recurrence: str  # Type can be adjusted based on needs
    endDateTime: str  # Assuming datetime will be passed as a string
    startDateTime: str  # Assuming datetime will be passed as a string
    autoReloadPartial: bool
    log: str
    state: str
    userId: str
    spaceId: str
    tenantId: str
    fortressId: str
    lastExecutionTime: str  # Assuming datetime will be passed as a string
    nextExecutionTime: str  # Assuming datetime will be passed as a string
    tenant_id: str

class ReloadTaskResponse(ReloadTaskCreate):
    id: str
