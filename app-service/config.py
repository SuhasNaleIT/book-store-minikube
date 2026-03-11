# app-service/config.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from app-service directory only
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

class Config:
    # ── Security ──────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-dev-secret")

    # ── Database ──────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://app_user:app_pass@localhost:5432/app_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Catalogue Service ─────────────────────────────────────
    CATALOGUE_SERVICE_URL = os.environ.get(
        "CATALOGUE_SERVICE_URL",
        "http://localhost:5002"
    )


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True

    # ── Isolated in-memory test DB ────────────────────────────
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # ── Point to a mock/test catalogue service ────────────────
    CATALOGUE_SERVICE_URL = "http://localhost:5002"

    # ── Disable CSRF for form tests ───────────────────────────
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False


# ── Config selector ───────────────────────────────────────────
config_map = {
    "development": DevelopmentConfig,
    "testing":     TestingConfig,
    "production":  ProductionConfig,
}

def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
