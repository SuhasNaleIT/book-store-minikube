# app-service/tests/conftest.py

import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from app.extensions import db as _db
from app.models import User, Order, OrderItem


# ─────────────────────────────────────────────────────────────
# MOCK BOOK DATA
# Simulates responses from catalogue-service.
# Tests never make real HTTP calls.
# ─────────────────────────────────────────────────────────────
MOCK_BOOK_1 = {
    "id":     1,
    "title":  "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "price":  9.99,
    "stock":  10,
    "isbn":   "978-0743273565"
}

MOCK_BOOK_2 = {
    "id":     2,
    "title":  "1984",
    "author": "George Orwell",
    "price":  7.99,
    "stock":  5,
    "isbn":   "978-0451524935"
}

MOCK_BOOKS = [MOCK_BOOK_1, MOCK_BOOK_2]


# ─────────────────────────────────────────────────────────────
# APP FIXTURE
# Creates a fresh app in testing mode for each test session.
# Uses SQLite in-memory DB — no PostgreSQL needed for tests.
# ─────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def app():
    test_app = create_app()
    test_app.config.update({
        "TESTING":                True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED":        False,
        "SECRET_KEY":              "test-secret-key",
        "CATALOGUE_SERVICE_URL":   "http://localhost:5002"
    })

    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


# ─────────────────────────────────────────────────────────────
# CLIENT FIXTURE
# Provides a test HTTP client for route testing.
# ─────────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


# ─────────────────────────────────────────────────────────────
# DB FIXTURE
# Wraps each test in a transaction that rolls back after.
# Keeps tests fully isolated — no leftover data between tests.
# ─────────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()


# ─────────────────────────────────────────────────────────────
# USER FIXTURES
# ─────────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def test_user(db):
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope="function")
def logged_in_client(client, test_user):
    """Returns a test client with a logged-in session."""
    client.post("/login", data={
        "email":    "test@example.com",
        "password": "password123"
    }, follow_redirects=True)
    return client


# ─────────────────────────────────────────────────────────────
# CATALOGUE SERVICE MOCK FIXTURES
# All HTTP calls to catalogue-service are intercepted here.
# Tests never hit a real network.
# ─────────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def mock_catalogue_books():
    """Mocks GET /api/books — returns list of all books."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_BOOKS

    with patch("requests.get", return_value=mock_resp) as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_catalogue_single_book():
    """Mocks GET /api/books/<id> — returns a single book."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_BOOK_1

    with patch("requests.get", return_value=mock_resp) as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_catalogue_unavailable():
    """Mocks catalogue-service being down — raises RequestException."""
    with patch(
        "requests.get",
        side_effect=Exception("Connection refused")
    ) as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_stock_patch_success():
    """Mocks PATCH /api/books/<id>/stock — returns 200 OK."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"message": "Stock updated"}

    with patch("requests.patch", return_value=mock_resp) as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_stock_patch_fail():
    """Mocks PATCH /api/books/<id>/stock — returns 400."""
    mock_resp = MagicMock()
    mock_resp.status_code = 400

    with patch("requests.patch", return_value=mock_resp) as mock:
        yield mock


# ─────────────────────────────────────────────────────────────
# ORDER FIXTURE
# Creates a test order with one item for order history tests.
# ─────────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def test_order(db, test_user):
    order = Order(
        user_id     = test_user.id,
        total_price = 9.99,
        status      = "paid"
    )
    db.session.add(order)
    db.session.flush()

    item = OrderItem(
        order_id          = order.id,
        book_id           = 1,
        quantity          = 1,
        price_at_purchase = 9.99
    )
    db.session.add(item)
    db.session.commit()
    return order
