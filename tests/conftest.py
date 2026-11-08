"""
Pytest Fixtures for AttendSync
------------------------------
Configures isolated test application and database contexts.
"""

import pytest
from app import create_app, db
from app.models import Student, AttendanceRecord


@pytest.fixture
def app():
    """Create and configure a testing instance of the Flask application."""
    test_app = create_app("testing")

    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Provides a test client for dispatching HTTP requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Provides a CLI runner for testing Flask CLI commands."""
    return app.test_cli_runner()
