from app import db

# Association table
user_tenants = db.Table('user_tenants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('tenant_id', db.String, db.ForeignKey('tenant.id'), primary_key=True)
)