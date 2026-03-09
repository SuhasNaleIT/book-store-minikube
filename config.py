import os       # lets you read environment variables

from dotenv import load_dotenv      # this function reads .env file

load_dotenv()
# reads the .env file and loads all
# KEY=VALUE pairs into environment variables

class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-key')
    # reads SECRET_KEY from your .env file
    # 'fallback-key' is used ONLY if SECRET_KEY is missing from .env (safety net)

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # reads DATABASE_URL from your .env file
    # this tells SQLAlchemy how to connect to PostgreSQL

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLAlchemy has a feature that tracks every
    # object change in memory — it's slow and
    # unnecessary, so we turn it off
    # Flask will show a warning if you don't set this
