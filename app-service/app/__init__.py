# app-service/app/__init__.py

import requests
from flask import (
    Flask, Blueprint, render_template, flash,
    request, current_app, session, redirect, url_for
)
from .extensions import db, login_manager, bcrypt, csrf
from config import get_config


# ─────────────────────────────────────────────────────────────
# MAIN BLUEPRINT
# ─────────────────────────────────────────────────────────────
main = Blueprint("main", __name__)


@main.route("/")
def home():
    """Redirects to books listing — single source of truth."""
    return redirect(url_for("main.books"))


@main.route("/books")
def books():
    """Books listing page with optional search."""
    search = request.args.get("search", "").strip()
    try:
        params = {"search": search} if search else {}
        resp   = requests.get(
            f"{current_app.config['CATALOGUE_SERVICE_URL']}/api/books",
            params=params,
            timeout=5
        )
        books = resp.json() if resp.status_code == 200 else []
    except requests.exceptions.RequestException:
        books = []
        flash("Catalogue service unavailable. Please try again later.", "warning")

    return render_template("main/books.html", books=books, search=search)


@main.route("/books/<int:book_id>")
def book_detail(book_id):
    """Single book detail page."""
    try:
        resp = requests.get(
            f"{current_app.config['CATALOGUE_SERVICE_URL']}/api/books/{book_id}",
            timeout=5
        )
        book = resp.json() if resp.status_code == 200 else None
    except requests.exceptions.RequestException:
        book = None
        flash("Catalogue service unavailable.", "warning")

    if not book:
        return render_template("errors/404.html"), 404

    return render_template("main/book_detail.html", book=book)


# ─────────────────────────────────────────────────────────────
# APPLICATION FACTORY
# ─────────────────────────────────────────────────────────────
def create_app():
    app = Flask(__name__)

    # ── Load config ───────────────────────────────────────────
    app.config.from_object(get_config())

    # ── Initialise extensions ─────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # ── Register blueprints ───────────────────────────────────
    from .auth.routes import auth
    from .cart.routes import cart

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(cart)

    # ── Create DB tables if they don't exist ──────────────────
    with app.app_context():
        db.create_all()

    # ── Context processor ─────────────────────────────────────
    @app.context_processor
    def inject_cart_count():
        cart  = session.get("cart", {})
        count = sum(cart.values()) if cart else 0
        return dict(cart_item_count=count)

    # ── Custom error pages ────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app
