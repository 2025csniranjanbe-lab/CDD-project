"""
AttendSync Extensions Module
----------------------------
Instantiates shared Flask extensions to eliminate circular dependencies.
Configures SQLite engine event listeners for foreign key constraint enforcement.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Initialize SQLAlchemy ORM instance
db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Ensures SQLite enforces foreign key constraints and cascades.
    By default, SQLite disables foreign key checks unless explicitly enabled.
    """
    if "sqlite" in type(dbapi_connection).__module__.lower():
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
