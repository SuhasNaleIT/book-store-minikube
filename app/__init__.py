# app/__init__.py
# ─────────────────────────────────────────────────────────────
# PURPOSE: App Factory — creates and configures the Flask app.
# teammates add their blueprints (catalogue, cart etc.)
# by registering them inside create_app().
# ─────────────────────────────────────────────────────────────

from flask import Flask
from config import Config


def create_app():
    # ─────────────────────────────────────────────
    # CREATE FLASK APP
    # __name__ tells Flask where this file lives —
    # used to locate templates/ and static/ folders.
    # ─────────────────────────────────────────────
    app = Flask(__name__)

    # Load config from config.py
    app.config.from_object(Config)

    # ─────────────────────────────────────────────
    # ROOT ROUTE — Hello World
    # Minimal route to confirm the app is running.
    # Will be replaced with blueprint routes later.
    # ─────────────────────────────────────────────
    @app.route('/')
    def index():
        return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>BookStore</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f8f9fa;
                }
                .box {
                    text-align: center;
                    padding: 40px 60px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                }
                h1 { color: #2c3e50; margin-bottom: 8px; }
                p  { color: #7f8c8d; }
            </style>
        </head>
        <body>
            <div class="box">
                <h1>📚 BookStore</h1>
                <p>Flask app is running successfully.</p>
                <p><strong>Hello, World!</strong></p>
            </div>
        </body>
        </html>
        '''

    # ─────────────────────────────────────────────
    # HEALTH CHECK
    # Required later by Kubernetes liveness probe.
    # Returns 200 if app is alive.
    # ─────────────────────────────────────────────
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200

    return app
