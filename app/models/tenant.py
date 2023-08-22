# app/models/tenant.py

from app import db
from app.models.associations import user_tenants
from sqlalchemy.orm import relationship

class Tenant(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    hostnames = db.Column(db.String(500), nullable=True)
    createdByUser = db.Column(db.String(255), nullable=True)
    datacenter = db.Column(db.String(255), nullable=True)
    created = db.Column(db.String(255), nullable=True)
    lastUpdated = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(255), nullable=True)
    autoAssignCreateSharedSpacesRoleToProfessionals = db.Column(db.Boolean, nullable=True)
    autoAssignPrivateAnalyticsContentCreatorRoleToProfessionals = db.Column(db.Boolean, nullable=True)
    autoAssignDataServicesContributorRoleToProfessionals = db.Column(db.Boolean, nullable=True)
    enableAnalyticCreation = db.Column(db.Boolean, nullable=True)
    qlik_cloud_api_key = db.Column(db.String(500))
    users = db.relationship('User', secondary=user_tenants, overlaps="tenants")