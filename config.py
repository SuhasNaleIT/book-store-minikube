# config.py
# ─────────────────────────────────────────────────────────────
# PURPOSE: Central configuration for the Flask app.
# Reads values from the .env file via python-dotenv.
# All settings are stored here — never scattered in routes.
# ─────────────────────────────────────────────────────────────

import os
from dotenv import load_dotenv

# Load all variables from .env into the environment
load_dotenv()


class Config:
    # ─────────────────────────────────────────────
    # SECRET_KEY
    # Used by Flask to sign session cookies securely.
    # Must be a long random string in production.
    # Reads from .env — falls back to 'dev-key' locally.
    # ─────────────────────────────────────────────
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

    # ─────────────────────────────────────────────
    # DATABASE_URL
    # PostgreSQL connection string.
    # Will be used when database is added later.
    # ─────────────────────────────────────────────
    DATABASE_URL = os.getenv('DATABASE_URL', '')
