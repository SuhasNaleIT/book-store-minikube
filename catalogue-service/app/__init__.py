import time
from flask import Flask, jsonify
from .extensions import db, migrate
from config import get_config


def create_app(test_config=None):
    app = Flask(__name__)

    # ── Load config ───────────────────────────────────────────
    app.config.from_object(get_config())

    # ── Override with test config if provided ─────────────────
    if test_config:
        app.config.update(test_config)

    # ── Initialise extensions ─────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)

    # ── Register blueprints ───────────────────────────────────
    from .catalogue.routes import catalogue
    app.register_blueprint(catalogue)

    # ── Create tables + seed with retry ───────────────────────
    with app.app_context():
        _init_db(app, test_config)

    # ── Health check endpoint ─────────────────────────────────
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "catalogue-service"}), 200

    # ── Error handlers ────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


# ─────────────────────────────────────────────────────────────
# DB INIT WITH RETRY
# Docker starts containers in order but PostgreSQL needs a few
# extra seconds to be truly ready — this retries instead of
# crashing immediately on startup.
# ─────────────────────────────────────────────────────────────
def _init_db(app, test_config=None):
    retries = 5
    for attempt in range(retries):
        try:
            db.create_all()
            if not test_config:         # skip seeding during tests
                _seed_books()
            return
        except Exception as e:
            if attempt < retries - 1:
                print(f"DB not ready (attempt {attempt + 1}/{retries}) — retrying in 3s... {e}")
                time.sleep(3)
            else:
                print("Could not connect to database after retries.")
                raise


# ─────────────────────────────────────────────────────────────
# SEED DATA
# Runs once on startup — only inserts if table is empty.
# ─────────────────────────────────────────────────────────────
def _seed_books():
    from .models import Book

    if Book.query.count() > 0:
        return  # Already seeded — skip

    books = [
        Book(
            title       = "1984",
            author      = "George Orwell",
            price       = 7.99,
            stock       = 10,
            cover       = "#e74c3c",
            isbn        = "978-0451524935",
            description = "A dystopian novel set in a totalitarian society "
                          "ruled by Big Brother, exploring surveillance, "
                          "propaganda and the loss of individual freedom."
        ),
        Book(
            title       = "The Great Gatsby",
            author      = "F. Scott Fitzgerald",
            price       = 9.99,
            stock       = 5,
            cover       = "#3498db",
            isbn        = "978-0743273565",
            description = "A tale of wealth, obsession and the American Dream "
                          "set in the Jazz Age, following the mysterious "
                          "millionaire Jay Gatsby."
        ),
        Book(
            title       = "To Kill a Mockingbird",
            author      = "Harper Lee",
            price       = 8.99,
            stock       = 8,
            cover       = "#2ecc71",
            isbn        = "978-0061935466",
            description = "A powerful story of racial injustice and moral "
                          "growth in the American South, seen through the "
                          "eyes of young Scout Finch."
        ),
        Book(
            title       = "Brave New World",
            author      = "Aldous Huxley",
            price       = 6.99,
            stock       = 15,
            cover       = "#9b59b6",
            isbn        = "978-0060850524",
            description = "A chilling vision of a future society where humans "
                          "are engineered and conditioned, exploring themes "
                          "of freedom, identity and technology."
        ),
        Book(
            title       = "The Hobbit",
            author      = "J.R.R. Tolkien",
            price       = 11.99,
            stock       = 3,
            cover       = "#f39c12",
            isbn        = "978-0261102217",
            description = "The beloved fantasy adventure of Bilbo Baggins, "
                          "a homebody hobbit who embarks on an unexpected "
                          "journey with a wizard and thirteen dwarves."
        ),
        Book(
            title       = "Dune",
            author      = "Frank Herbert",
            price       = 10.99,
            stock       = 7,
            cover       = "#1abc9c",
            isbn        = "978-0441013593",
            description = "An epic science fiction saga set on the desert "
                          "planet Arrakis, following Paul Atreides as he "
                          "navigates politics, religion and destiny."
        ),
    ]

    db.session.add_all(books)
    db.session.commit()
    print("catalogue-service: 6 books seeded successfully.")
