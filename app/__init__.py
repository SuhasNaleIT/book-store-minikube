# app/__init__.py

# PURPOSE: App Factory — creates and configures the Flask app.
# This is the central file that wires together:
#   - Configuration (config.py)
#   - Extensions (db, bcrypt, login_manager)
#   - Blueprints (auth, catalogue, cart)
#   - Root route (/)

from flask_login import current_user
from flask import Flask, redirect, url_for
from config import Config
from app.extensions import db, bcrypt, login_manager


def create_app():

    # CREATE FLASK APP
    # __name__ tells Flask where to look for templates/static
    # files — it uses the location of this file as reference

    app = Flask(__name__)

    # LOAD CONFIGURATION
    # Reads all settings from config.py (Config class)
    # Sets SECRET_KEY, DATABASE_URL etc. on the app

    app.config.from_object(Config)

    # INITIALISE EXTENSIONS
    # Connect each extension to the Flask app.
    # Extensions were created in extensions.py WITHOUT an app.
    # init_app() connects them to THIS specific app now.
    # This is why we separated extensions.py — avoids
    # circular imports.

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # REGISTER BLUEPRINTS
    # Blueprints are mini apps that hold related routes.
    # We import them HERE (inside the function) to avoid
    # circular imports — routes need app, app needs routes.
    # Importing inside create_app() breaks the circular chain.

    # Auth blueprint — handles /signup, /login, /logout
    from app.auth.routes import auth
    app.register_blueprint(auth)

    # Catalogue blueprint — handles /books, /books/<id>
    # We will create this file later
    
    #**** UNCOMMENT THIS WHEN WE CREATE THE CATALOGUE BLUEPRINT ****
    
    from app.catalogue.routes import catalogue
    app.register_blueprint(catalogue)

    # Cart blueprint — handles /cart, /cart/add, /checkout
    # We will create this file later

    #**** UNCOMMENT THIS WHEN WE CREATE THE CART BLUEPRINT ****

    from app.cart.routes import cart
    app.register_blueprint(cart)

    # ROOT ROUTE
    # Handles http://localhost:5000/
    # Redirects based on login status:
    #   logged in  → /books (catalogue page)
    #   logged out → /books (public, no login needed)
    # We define it here because it belongs to the main app,
    # not to any specific blueprint.

    @app.route('/')
    def index():
        # both logged in and logged out users see books
        # (Amazon-style — public catalogue)
        return redirect(url_for('catalogue.books'))

    # HEALTH CHECK ROUTE
    # Required by Kubernetes liveness probe.
    # Kubernetes calls this every few seconds to check
    # if the app is alive. Must return 200 status.
    # No login required — Kubernetes has no user session.

    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200

    # READINESS CHECK ROUTE
    # Required by Kubernetes readiness probe.
    # Kubernetes calls this to check if app is ready
    # to receive traffic (DB connected, etc.)
    # Returns 200 if ready, 503 if not ready.

    @app.route('/ready')
    def ready():
        try:
            # try a simple database query to verify
            # PostgreSQL connection is working
            db.session.execute(db.text('SELECT 1'))
            return {'status': 'ready'}, 200
        except Exception:
            # DB not reachable — not ready for traffic yet
            return {'status': 'not ready'}, 503

    # CACHE CONTROL
    # 'private' means:
    # - Browser CAN cache the page locally (Back button works fast)
    # - CDN / shared proxies CANNOT cache it (secure)
    #
    # This allows smooth Back navigation while logged in.
    # Cache is wiped on logout via Clear-Site-Data header.

    @app.after_request
    def set_cache_control(response):
        if current_user.is_authenticated:
            # private = only browser cache, not shared/CDN cache
            response.headers['Cache-Control'] = 'private'
        else:
            # Public pages (catalogue, login, signup) can be
            # cached normally — no sensitive data on these pages
            response.headers['Cache-Control'] = 'public, max-age=300'
            # max-age=300 = cache for 5 minutes
        return response
    

    # CONTEXT PROCESSOR — Cart Item Count
    #
    # A context processor runs before every template render
    # and injects variables that are available in ALL templates.
    #
    # Why we need this:
    # The cart count badge in base.html must show on EVERY page
    # (books list, book detail, checkout etc.)
    # Without a context processor, we would have to pass
    # cart_item_count manually in every single route — messy.
    #
    # With this, every template automatically has access to
    # {{ cart_item_count }} without any route needing to pass it.
    #
    # We count distinct cart items (rows) not total quantity.
    # e.g. 3 different books = badge shows 3

    @app.context_processor
    def inject_cart_count():
        # Only query if user is logged in
        # Anonymous users have no cart
        if current_user.is_authenticated:
            from app.models import CartItem
            # Count number of distinct items (rows) in cart
            # not the total quantity across all items
            count = CartItem.query.filter_by(
                user_id=current_user.id
            ).count()
            return {'cart_item_count': count}
        # Not logged in → return 0 so template doesn't crash
        return {'cart_item_count': 0}

    # return the fully configured app
    return app
