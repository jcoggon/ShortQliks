from app import db

class ReloadTask(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    appId = db.Column(db.String(255), nullable=False)
    partial = db.Column(db.Boolean, default=False)
    timeZone = db.Column(db.String(255))
    autoReload = db.Column(db.Boolean, default=False)
    recurrence = db.Column(db.PickleType)  # Use PickleType to store a list
    endDateTime = db.Column(db.DateTime, nullable=True)
    startDateTime = db.Column(db.DateTime, nullable=True)
    autoReloadPartial = db.Column(db.Boolean, default=False)
    log = db.Column(db.Text)
    state = db.Column(db.String(255))
    userId = db.Column(db.String(255), nullable=False)
    spaceId = db.Column(db.String(255), nullable=True)
    tenantId = db.Column(db.String(255), nullable=True)
    fortressId = db.Column(db.String(255), nullable=True)
    lastExecutionTime = db.Column(db.DateTime, nullable=True)
    nextExecutionTime = db.Column(db.DateTime, nullable=True)
    tenant_id = db.Column(db.String, db.ForeignKey('tenant.id'))  # Add this line

    def to_dict(self):
        return {
            'id': self.id,
            'appId': self.appId,
            'partial': self.partial,
            'timeZone': self.timeZone,
            'autoReload': self.autoReload,
            'recurrence': self.recurrence if self.recurrence else [],
            'endDateTime': self.endDateTime.strftime('%Y-%m-%dT%H:%M:%S') if self.endDateTime else None,
            'startDateTime': self.startDateTime.strftime('%Y-%m-%dT%H:%M:%S') if self.startDateTime else None,
            'autoReloadPartial': self.autoReloadPartial,
            'log': self.log,
            'state': self.state,
            'userId': self.userId,
            'spaceId': self.spaceId,
            'tenantId': self.tenantId,
            'fortressId': self.fortressId,
            'lastExecutionTime': self.lastExecutionTime.strftime('%Y-%m-%dT%H:%M:%S') if self.lastExecutionTime else None,
            'nextExecutionTime': self.nextExecutionTime.strftime('%Y-%m-%dT%H:%M:%S') if self.nextExecutionTime else None,
            'tenant_id': self.tenant_id
        }