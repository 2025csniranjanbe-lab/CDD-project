"""
Main Blueprint & Health Check Routes
------------------------------------
Defines the baseline entry routes, landing page, and system health check endpoints.
"""

from datetime import datetime, timezone
from flask import Blueprint, jsonify, render_template, current_app

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """
    Landing / Dashboard entry point.
    Renders the baseline HTML page confirming system operation.
    """
    return render_template(
        "index.html",
        system_status="AttendSync System Online",
        environment=current_app.config.get("ENV", "development"),
        database_uri=current_app.config.get("SQLALCHEMY_DATABASE_URI"),
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    )


@main_bp.route("/health")
def health_check():
    """
    Baseline Health Check Endpoint.
    Used for uptime monitoring, CI/CD pipelines, and Docker container HEALTHCHECK.
    """
    return jsonify({
        "status": "online",
        "message": "AttendSync System Online",
        "service": "AttendSync - Dockerized Attendance Management System",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "sqlite_connected"
    }), 200
