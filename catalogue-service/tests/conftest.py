import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    """Create a catalogue-service test app with an in-memory SQLite DB."""
    test_config = {
        "TESTING":                        True,
        "SQLALCHEMY_DATABASE_URI":        "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY":                     "test_secret_key",
    }

    app = create_app(test_config)

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="session")
def client(app):
    """Flask test client for the catalogue-service."""
    return app.test_client()


@pytest.fixture(scope="function")
def db(app):
    """
    Gives each test a clean database state.
    Rolls back after every test — no leftover data.
    """
    with app.app_context():
        yield _db
        _db.session.rollback()
