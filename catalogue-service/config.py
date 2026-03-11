# catalogue-service/config.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from catalogue-service directory only
# Prevents picking up parent directory .env files (e.g. monolith)
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)


class Config:
    # ── Security ──────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-dev-secret")

    # ── Database ──────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://bookstore_user:bookstore_pass@localhost:5433/catalogue_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── API behaviour ─────────────────────────────────────────
    JSON_SORT_KEYS = False          # preserve field order in JSON responses


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG   = True

    # ── Isolated in-memory test DB ────────────────────────────
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


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
