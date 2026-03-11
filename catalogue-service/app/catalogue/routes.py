# catalogue-service/app/catalogue/routes.py

from flask import Blueprint, jsonify, request
from ..extensions import db
from ..models import Book

catalogue = Blueprint("catalogue", __name__)


# ─────────────────────────────────────────────────────────────
# GET /api/books
# Returns all books. Supports optional ?search= query param.
# Public endpoint — no auth required.
# ─────────────────────────────────────────────────────────────
@catalogue.route("/api/books", methods=["GET"])
def get_books():
    search = request.args.get("search", "").strip()

    if search:
        books = Book.query.filter(
            db.or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%")
            )
        ).all()
    else:
        books = Book.query.order_by(Book.created_at.desc()).all()

    return jsonify([book.to_dict() for book in books]), 200


# ─────────────────────────────────────────────────────────────
# GET /api/books/<id>
# Returns a single book by ID.
# Returns 404 if not found.
# ─────────────────────────────────────────────────────────────
@catalogue.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get(book_id)

    if not book:
        return jsonify({"error": "Book not found"}), 404

    return jsonify(book.to_dict()), 200


# ─────────────────────────────────────────────────────────────
# POST /api/books
# Creates a new book.
# Required fields: title, author, price, stock
# Optional fields: description, isbn, cover
# ─────────────────────────────────────────────────────────────
@catalogue.route("/api/books", methods=["POST"])
def create_book():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # ── Validate required fields ──────────────────────────────
    required = ["title", "author", "price", "stock"]
    missing  = [f for f in required if f not in data]
    if missing:
        return jsonify({
            "error": f"Missing required fields: {', '.join(missing)}"
        }), 400

    # ── Validate types ────────────────────────────────────────
    try:
        price = float(data["price"])
        stock = int(data["stock"])
    except (ValueError, TypeError):
        return jsonify({"error": "price must be a number, stock must be an integer"}), 400

    if price < 0:
        return jsonify({"error": "price cannot be negative"}), 400
    if stock < 0:
        return jsonify({"error": "stock cannot be negative"}), 400

    book = Book(
        title       = data["title"].strip(),
        author      = data["author"].strip(),
        price       = price,
        stock       = stock,
        description = data.get("description", "").strip() or None,
        isbn        = data.get("isbn", "").strip() or None,
        cover       = data.get("cover", "#6c757d")
    )

    db.session.add(book)
    db.session.commit()

    return jsonify(book.to_dict()), 201


# ─────────────────────────────────────────────────────────────
# PATCH /api/books/<id>
# Updates one or more fields of an existing book.
# Only updates fields that are present in the request body.
# ─────────────────────────────────────────────────────────────
@catalogue.route("/api/books/<int:book_id>", methods=["PATCH"])
def update_book(book_id):
    book = Book.query.get(book_id)

    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # ── Apply only fields present in request ──────────────────
    if "title"       in data: book.title       = data["title"].strip()
    if "author"      in data: book.author      = data["author"].strip()
    if "description" in data: book.description = data["description"].strip() or None
    if "isbn"        in data: book.isbn        = data["isbn"].strip() or None
    if "cover"       in data: book.cover       = data["cover"]

    if "price" in data:
        try:
            price = float(data["price"])
            if price < 0:
                return jsonify({"error": "price cannot be negative"}), 400
            book.price = price
        except (ValueError, TypeError):
            return jsonify({"error": "price must be a number"}), 400

    if "stock" in data:
        try:
            stock = int(data["stock"])
            if stock < 0:
                return jsonify({"error": "stock cannot be negative"}), 400
            book.stock = stock
        except (ValueError, TypeError):
            return jsonify({"error": "stock must be an integer"}), 400

    db.session.commit()
    return jsonify(book.to_dict()), 200


# ─────────────────────────────────────────────────────────────
# PATCH /api/books/<id>/stock
# Dedicated stock decrement endpoint — called by app-service
# at checkout time only.
# Body: { "quantity": <int> }   ← amount to decrement
# ─────────────────────────────────────────────────────────────
@catalogue.route("/api/books/<int:book_id>/stock", methods=["PATCH"])
def update_stock(book_id):
    book = Book.query.get(book_id)

    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json()
    if not data or "quantity" not in data:
        return jsonify({"error": "quantity is required"}), 400

    try:
        quantity = int(data["quantity"])
    except (ValueError, TypeError):
        return jsonify({"error": "quantity must be an integer"}), 400

    if quantity <= 0:
        return jsonify({"error": "quantity must be positive"}), 400

    if book.stock < quantity:
        return jsonify({
            "error":     "Insufficient stock",
            "available": book.stock
        }), 400

    book.stock -= quantity
    db.session.commit()

    return jsonify({
        "message":       "Stock updated",
        "book_id":       book.id,
        "stock_remaining": book.stock
    }), 200


# ─────────────────────────────────────────────────────────────
# DELETE /api/books/<id>
# Deletes a book permanently.
# ─────────────────────────────────────────────────────────────
@catalogue.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get(book_id)

    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({"message": f'Book "{book.title}" deleted successfully'}), 200
