# run.py

# This file:
#   1. Calls create_app() to build the Flask app
#   2. Creates all database tables if they don't exist
#   3. Starts the development server
#

from app import create_app
from app.extensions import db
from app.models import Book

app = create_app()

if __name__ == '__main__':

    with app.app_context():

        # ─────────────────────────────────────────────
        # CREATE TABLES
        # Creates all tables defined in models.py.
        # If a table already exists, it skips it safely.
        # So running this multiple times is safe.
        # ─────────────────────────────────────────────
        db.create_all()
        # ─────────────────────────────────────────────
        # SEED SAMPLE BOOKS
        # Only seeds if the books table is currently empty.
        # This prevents duplicate entries on every restart.
        # ─────────────────────────────────────────────
        if Book.query.count() == 0:
            sample_books = [
                Book(
                    title='Clean Code',
                    author='Robert C. Martin',
                    price=29.99,
                    stock=10,
                    description='A handbook of agile software craftsmanship. '
                                'Learn how to write readable, maintainable code.',
                    cover='#e74c3c'
                ),
                Book(
                    title='The Pragmatic Programmer',
                    author='Andrew Hunt',
                    price=34.99,
                    stock=5,
                    description='Your journey to mastery. Timeless lessons for '
                                'developers at all skill levels.',
                    cover='#2980b9'
                ),
                Book(
                    title='Designing Data-Intensive Applications',
                    author='Martin Kleppmann',
                    price=44.99,
                    stock=8,
                    description='The big ideas behind reliable, scalable, '
                                'and maintainable systems.',
                    cover='#27ae60'
                ),
                Book(
                    title='Docker Deep Dive',
                    author='Nigel Poulton',
                    price=19.99,
                    stock=15,
                    description='A fast, focused introduction to Docker '
                                'containers and the container ecosystem.',
                    cover='#8e44ad'
                ),
                Book(
                    title='Kubernetes in Action',
                    author='Marko Luksa',
                    price=49.99,
                    stock=0,   # ← out of stock demo
                    description='A comprehensive guide to deploying and '
                                'managing applications in Kubernetes.',
                    cover='#e67e22'
                ),
            ]

            db.session.bulk_save_objects(sample_books)
            db.session.commit()
            print('✅ Sample books seeded successfully.')
        else:
            print('ℹ️  Books already exist — skipping seed.')
            print('✅ Database tables created/verified')

    # start the Flask development server
    # debug=True means:
    #   - auto reloads when you save a file
    #   - shows detailed error pages in browser
    #   - NEVER use debug=True in production
    # host='0.0.0.0' means accessible from any network
    #   interface — needed later for Docker
    # port=5000 is the default Flask port
    app.run(debug=True, host='0.0.0.0', port=5000)
