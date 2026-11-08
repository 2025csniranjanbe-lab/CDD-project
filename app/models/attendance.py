"""
Attendance Record Model
-----------------------
Tracks check-in events and attendance statuses for users.
"""

from datetime import datetime, timezone
from app.extensions import db


class Attendance(db.Model):
    __tablename__ = "attendance_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="present")  # 'present', 'absent', 'late', 'excused'
    notes = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        """Serialize attendance record to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "notes": self.notes
        }

    def __repr__(self):
        return f"<Attendance user_id={self.user_id} status={self.status} at={self.timestamp}>"
