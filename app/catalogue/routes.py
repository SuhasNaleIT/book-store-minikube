# app/catalogue/routes.py
# ─────────────────────────────────────────────────────────────
# PURPOSE: Handle all catalogue (books) routes.
# /books         → list all books (PUBLIC — no login needed)
# /books/<id>    → single book detail (PUBLIC)
#
# The catalogue is publicly visible — just like Amazon.
# Users do NOT need to log in to browse books.
# Login is only required at checkout (handled in cart blueprint).
# ─────────────────────────────────────────────────────────────

from flask import render_template, Blueprint
from flask_login import current_user
from app.models import Book


# ─────────────────────────────────────────────────────────────
# BLUEPRINT
# Name 'catalogue' is used in url_for('catalogue.books')
# Consistent with how 'auth' is defined in auth/routes.py
# ─────────────────────────────────────────────────────────────
catalogue = Blueprint('catalogue', __name__)


# ─────────────────────────────────────────────────────────────
# BOOKS LISTING ROUTE
# GET /books → shows all books from the database as cards.
# NO @login_required — public page, anyone can view.
# current_user is passed so the template can show
# Login/Logout in the navbar correctly.
# ─────────────────────────────────────────────────────────────
@catalogue.route('/books')
def books():
    # Query ALL books from the 'books' table in PostgreSQL.
    # .all() returns a Python list of Book objects.
    # If table is empty, returns an empty list (no crash).
    all_books = Book.query.order_by(Book.id).all()

    return render_template(
        'catalogue/books.html',
        books=all_books,
        user=current_user   # passed so navbar knows login state
    )


# ─────────────────────────────────────────────────────────────
# BOOK DETAIL ROUTE
# GET /books/<id> → shows a single book's full detail.
# get_or_404 returns the book if found, or a 404 error page.
# ─────────────────────────────────────────────────────────────
@catalogue.route('/books/<int:book_id>')
def book_detail(book_id):
    # get_or_404 is a SQLAlchemy helper:
    # if book with this id exists → return it
    # if not found → automatically return HTTP 404 page
    book = Book.query.get_or_404(book_id)

    return render_template(
        'catalogue/book_detail.html',
        book=book,
        user=current_user
    )
