"""
Models package initialization.
Exposes core models for clean imports across blueprints and services.
"""

from app.models import AttendanceRecord, AttendanceStatus, Student

__all__ = ["Student", "AttendanceRecord", "AttendanceStatus"]
