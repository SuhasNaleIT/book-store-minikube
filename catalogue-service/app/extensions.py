# catalogue-service/app/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# ── Instantiate extensions (not yet bound to any app) ─────────
db      = SQLAlchemy()
migrate = Migrate()
