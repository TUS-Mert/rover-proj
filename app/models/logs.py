from .. import db

class CommandLog(db.Model):
    __tablename__ = 'command_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    command = db.Column(db.String(100), nullable=False) # e.g., "FORWARD", "STOP"
    is_executed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    executed_at = db.Column(db.DateTime, nullable=True)