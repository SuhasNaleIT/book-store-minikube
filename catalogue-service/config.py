import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)


class Config:
    SECRET_KEY                     = os.environ.get("SECRET_KEY", "fallback-dev-secret")
    SQLALCHEMY_DATABASE_URI        = os.environ.get(
        "DATABASE_URL",
        "postgresql://bookstore_user:bookstore_pass@localhost:5433/catalogue_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS      = {
        "pool_pre_ping": True,      # retries dropped connections — critical for Docker
        "pool_recycle":  300,       # recycles connections every 5 mins
    }
    JSON_SORT_KEYS                 = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING                 = True
    DEBUG                   = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "testing":     TestingConfig,
    "production":  ProductionConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
