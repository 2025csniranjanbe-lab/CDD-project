"""
AttendSync Application Server Entry Point (WSGI)
------------------------------------------------
Provides the top-level application callable for production WSGI servers (e.g., Gunicorn, uWSGI)
and local development execution (`python wsgi.py`).
"""

import os
from app import create_app, db

# Determine active environment configuration
env_name = os.getenv("FLASK_ENV", "development")
app = create_app(env_name)

if __name__ == "__main__":
    # Ensure database schema is initialized for local development
    with app.app_context():
        db.create_all()

    # Port and host configurations
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug = app.config.get("DEBUG", True)

    print(f"\n==================================================")
    print(f" AttendSync Development Server Starting")
    print(f" Environment : {env_name}")
    print(f" Listening on: http://{host}:{port}")
    print(f" Health check: http://{host}:{port}/health")
    print(f"==================================================\n")

    app.run(host=host, port=port, debug=debug)
