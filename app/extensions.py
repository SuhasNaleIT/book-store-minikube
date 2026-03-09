# app/extensions.py

# PURPOSE: Create all Flask extension instances in ONE place.
# These are created here WITHOUT being tied to any Flask app yet.
# They get connected to the actual Flask app later in app/__init__.py
# using the init_app() pattern.
# This prevents circular imports across the project.

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


# SQLAlchemy instance — handles all database operations

db = SQLAlchemy()

# Handles password hashing
# Used in auth/routes.py to hash passwords on signup
# and verify passwords on login
bcrypt = Bcrypt()


# LoginManager instance — handles user sessions
# Tracks who is logged in across requests
# Redirects to login page if @login_required route is accessed
login_manager = LoginManager()

# Which route to redirect to when user is NOT logged in
# 'auth.login' means → Blueprint named 'auth', function named 'login'
login_manager.login_view = 'auth.login'

# Message shown to user when redirected to login page
login_manager.login_message = 'Please log in to access this page.'

# Bootstrap alert style for the message above
# 'warning' = yellow alert box
login_manager.login_message_category = 'warning'
