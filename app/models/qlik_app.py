from app import db

class QlikApp(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    owner = db.Column(db.String(255), nullable=True)  # Added nullable=True
    usage = db.Column(db.String(50), nullable=True)  # Added nullable=True
    ownerId = db.Column(db.String(255), nullable=True)  # Added nullable=True
    encrypted = db.Column(db.Boolean, nullable=True)  # Added nullable=True
    published = db.Column(db.Boolean, nullable=True)  # Added nullable=True
    thumbnail = db.Column(db.String(255), nullable=True)  # Added nullable=True
    createdDate = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)  # Added nullable=True
    originAppId = db.Column(db.String(255), nullable=True)  # Added nullable=True
    publishTime = db.Column(db.String(255), nullable=True)
    dynamicColor = db.Column(db.String(50), nullable=True)  # Added nullable=True
    modifiedDate = db.Column(db.String(255), nullable=True)
    lastReloadTime = db.Column(db.String(255), nullable=True)
    hasSectionAccess = db.Column(db.Boolean, nullable=True)  # Added nullable=True
    isDirectQueryMode = db.Column(db.Boolean, nullable=True)  # Added nullable=True
    tenant_id = db.Column(db.String, db.ForeignKey('tenant.id'))  # Add this line
