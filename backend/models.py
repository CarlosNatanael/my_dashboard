from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    console = db.Column(db.String(50), nullable=False)
    console_icon = db.Column(db.String(200), nullable=True) 
    ra_id = db.Column(db.Integer, nullable=True)
    image_icon = db.Column(db.String(100), nullable=True)

    status = db.Column(db.String(50), default='claim')
    progress = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    STATUS_MAP = {
        'wishlist': ('Wishlist (Future)', 'dark'),
        'jr_plan_review': ('Request Plan Review (Set Plan)', 'warning'),
        'jr_plan_wait': ('Awaiting Plan Approval', 'secondary'),
        'claim': ('Added to Claim', 'secondary'),
        'ram': ('Digging/Inspecting RAM', 'info'),
        'logic': ('Developing Achievements', 'primary'),
        'badge': ('Developing Badges/Icons', 'primary'),
        'writing': ('Awaiting Writing Review', 'warning'),
        'art_team': ('Awaiting Art Team', 'warning'),
        'playtest': ('Sent to Player-Tester', 'warning'),
        'test': ('Testing Achievements (Local)', 'light-dark text'),
        'pre_release': ('Final tests (Pre-Release)', 'success'),
        'jr_review_request': ('Request Set Review', 'warning'),
        'jr_queue': ('In Review Queue/Backlog', 'secondary'),
        'jr_cr_active': ('Reviewed by Code Reviewer', 'info'),
        'published': ('Published', 'success'),
        'tickets': ('Attending Tickets', 'danger'),
        'review': ('Set Review (Bugfix)', 'danger'),
        'jr_republish': ('Request Republishing (Postfix)', 'warning')
    }

    @property
    def status_label(self):
        return self.STATUS_MAP.get(self.status, (self.status, 'secondary'))[0]

    @property
    def status_color(self):
        return self.STATUS_MAP.get(self.status, ('secondary', 'secondary'))[1]