import time
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
def create_app(test_config=None):
    app = Flask(__name__)

    # ── Load config ───────────────────────────────────────────
    app.config.from_object(get_config())

    # ── Override with test config if provided ─────────────────
    if test_config:
        app.config.update(test_config)

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

    # ── Create DB tables with retry ───────────────────────────
    with app.app_context():
        _init_db()

    # ── Context processor ─────────────────────────────────────
    @app.context_processor
    def inject_cart_count():
        cart  = session.get("cart", {})
        count = sum(cart.values()) if cart else 0
        return dict(cart_item_count=count)
    
     # ── Health check endpoint ─────────────────────────────────
    @app.route("/health")
    def health():
        return {"status": "ok", "service": "app-service"}, 200

    # ── Custom error pages ────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app


# ─────────────────────────────────────────────────────────────
# DB INIT WITH RETRY
# Docker starts containers in order but PostgreSQL needs a few
# extra seconds to be truly ready — this retries instead of
# crashing immediately on startup.
# ─────────────────────────────────────────────────────────────
def _init_db():
    retries = 5
    for attempt in range(retries):
        try:
            db.create_all()
            return
        except Exception as e:
            if attempt < retries - 1:
                print(f"DB not ready (attempt {attempt + 1}/{retries}) — retrying in 3s... {e}")
                time.sleep(3)
            else:
                print("Could not connect to database after retries.")
                raise
