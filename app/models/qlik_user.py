from app import db

# Association tables
user_group_association = db.Table('user_group_association',
                                  db.Column('user_id', db.String, db.ForeignKey('qlik_user.id')),
                                  db.Column('group_id', db.String, db.ForeignKey('assigned_group.id'))
                                  )

user_role_association = db.Table('user_role_association',
                                db.Column('user_id', db.String, db.ForeignKey('qlik_user.id')),
                                db.Column('role_id', db.String, db.ForeignKey('assigned_role.id'))
                                )

class QlikUser(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True, default='N/A')
    tenantId = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(255), nullable=True)
    created = db.Column(db.DateTime, nullable=True)
    lastUpdated = db.Column(db.DateTime, nullable=True)
    qlik_app_link = db.Column(db.String(255), nullable=True)
    
    # Relationships
    groups = db.relationship('AssignedGroup', secondary=user_group_association, backref='users')
    roles = db.relationship('AssignedRole', secondary=user_role_association, backref='users')

class AssignedGroup(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=True)

class AssignedRole(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(255), nullable=True)
    level = db.Column(db.String(255), nullable=True)
    permissions = db.Column(db.String(255), nullable=True)  # Assuming permissions are stored as comma-separated values
