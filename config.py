"""
AttendSync Configuration Module
-------------------------------
Provides environment-specific configuration classes adhering to the 12-factor app methodology.
Handles SQLite database persistence across local and containerized environments.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base project directory
BASE_DIR = Path(__file__).resolve().parent

# Automatically load environment variables from .env if present
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base configuration containing shared defaults."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-attendsync-fallback-2026")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Persistent SQLite database storage inside the 'instance' folder
    INSTANCE_DIR = BASE_DIR / "instance"
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

    # Cross-platform SQLite URI (handles Windows backslashes and Linux paths)
    DEFAULT_DB_PATH = (INSTANCE_DIR / "attendsync.db").resolve().as_posix()
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")


class DevelopmentConfig(Config):
    """Configuration for local development."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Configuration for automated test suites."""
    DEBUG = False
    TESTING = True
    # Fast in-memory SQLite database for isolated test execution
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    """Configuration for production and Docker deployments."""
    DEBUG = False
    TESTING = False

    # In production, require an explicit SECRET_KEY
    SECRET_KEY = os.getenv("SECRET_KEY")


# Configuration dictionary lookup
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
