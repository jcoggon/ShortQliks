from app import db
from sqlalchemy.dialects.postgresql import JSON

class QlikSpace(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255))
    type = db.Column(db.String(255), nullable=True)
    owner_id = db.Column(db.String(255), nullable=True)
    tenant_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.Text, nullable=True)
    meta = db.Column(JSON, nullable=True)
    links = db.Column(JSON, nullable=True)
