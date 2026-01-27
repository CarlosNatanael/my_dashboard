from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    console = db.Column(db.String(50), nullable=False)
    console_icon = db.Column(db.String(200), nullable=True) 

    ra_id = db.Column(db.Integer, nullable=True)
    image_icon = db.Column(db.String(100), nullable=True)

    status = db.Column(db.String(20), default='backlog')
    progress = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Claim {self.title} - {self.status}>'