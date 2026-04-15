# catalogue-service/tests/test_catalogue.py

import json
import pytest
from app.models import Book


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def _add_book(db, **kwargs):
    """Insert a single book directly into the test DB."""
    defaults = dict(
        title       = "Test Book",
        author      = "Test Author",
        price       = 9.99,
        stock       = 5,
        cover       = "#ffffff",
        isbn        = "978-0000000000",
        description = "A test book description."
    )
    defaults.update(kwargs)
    book = Book(**defaults)
    db.session.add(book)
    db.session.commit()
    return book


# ─────────────────────────────────────────────────────────────
# GET /api/books
# ─────────────────────────────────────────────────────────────
class TestGetAllBooks:

    def test_returns_200(self, client, db):
        _add_book(db)
        response = client.get("/api/books")
        assert response.status_code == 200

    def test_returns_list(self, client, db):
        _add_book(db, title="Book A", isbn="978-0000000001")
        _add_book(db, title="Book B", isbn="978-0000000002")
        response = client.get("/api/books")
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_book_has_required_fields(self, client, db):
        _add_book(db, isbn="978-0000000003")
        response = client.get("/api/books")
        data = json.loads(response.data)
        book = data[0]
        for field in ["id", "title", "author", "price", "stock", "isbn"]:
            assert field in book


# ─────────────────────────────────────────────────────────────
# GET /api/books/<id>
# ─────────────────────────────────────────────────────────────
class TestGetSingleBook:

    def test_returns_200_for_existing_book(self, client, db):
        book = _add_book(db, isbn="978-0000000004")
        response = client.get(f"/api/books/{book.id}")
        assert response.status_code == 200

    def test_returns_correct_book(self, client, db):
        book = _add_book(db, title="Specific Book", isbn="978-0000000005")
        response = client.get(f"/api/books/{book.id}")
        data = json.loads(response.data)
        assert data["title"] == "Specific Book"

    def test_returns_404_for_missing_book(self, client, db):
        response = client.get("/api/books/99999")
        assert response.status_code == 404


# ─────────────────────────────────────────────────────────────
# GET /api/books/<id>/stock
# ─────────────────────────────────────────────────────────────
class TestGetStock:

    def test_returns_stock_value(self, client, db):
        book = _add_book(db, stock=7, isbn="978-0000000006")
        response = client.get(f"/api/books/{book.id}/stock")
        data = json.loads(response.data)
        assert data["stock"] == 7

    def test_returns_404_for_missing_book(self, client, db):
        response = client.get("/api/books/99999/stock")
        assert response.status_code == 404


# ─────────────────────────────────────────────────────────────
# PATCH /api/books/<id>/stock
# ─────────────────────────────────────────────────────────────
class TestUpdateStock:

    def test_reduces_stock_correctly(self, client, db):
        book = _add_book(db, stock=10, isbn="978-0000000007")
        response = client.patch(
            f"/api/books/{book.id}/stock",
            data        = json.dumps({"quantity": 3}),
            content_type= "application/json"
        )
        data = json.loads(response.data)
        assert data["stock"] == 7

    def test_returns_400_when_insufficient_stock(self, client, db):
        book = _add_book(db, stock=2, isbn="978-0000000008")
        response = client.patch(
            f"/api/books/{book.id}/stock",
            data        = json.dumps({"quantity": 10}),
            content_type= "application/json"
        )
        assert response.status_code == 400

    def test_returns_404_for_missing_book(self, client, db):
        response = client.patch(
            "/api/books/99999/stock",
            data        = json.dumps({"quantity": 1}),
            content_type= "application/json"
        )
        assert response.status_code == 404


# ─────────────────────────────────────────────────────────────
# GET /health
# ─────────────────────────────────────────────────────────────
class TestHealth:

    def test_health_check(self, client):
        response = client.get("/health")
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["status"] == "ok"
        assert data["service"] == "catalogue-service"
