# run.py
# ─────────────────────────────────────────────────────────────
# PURPOSE: Entry point to start the Flask application.
#
# HOW TO RUN:
#   python run.py
#
# App will be available at:
#   http://localhost:5000
# ─────────────────────────────────────────────────────────────

from app import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True  → auto-reloads on file save, shows error pages
    # host='0.0.0.0' → accessible from any network interface
    #                  (needed later for Docker)
    # port=5000   → default Flask port
    #
    # NEVER use debug=True in production
    app.run(debug=True, host='0.0.0.0', port=5000)
