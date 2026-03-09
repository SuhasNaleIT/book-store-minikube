# app/models.py

# PURPOSE: Define all database tables as Python classes.
# Each class = one table in PostgreSQL.
# SQLAlchemy reads these classes and creates/manages the tables.
# Flask-Login needs the User model to manage login sessions.

from flask_login import UserMixin
from app.extensions import db, login_manager

# USER LOADER
# Flask-Login needs this function to reload the user object
# from the session on every request.
# It takes a user_id (stored in the session cookie) and
# returns the User object from the database.

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# USER TABLE
# Stores registered users (customers and admins).
# UserMixin adds 4 required methods Flask-Login needs:
#   is_authenticated, is_active, is_anonymous, get_id

class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True        # auto-incrementing unique ID
    )
    name = db.Column(
        db.String(100),
        nullable=False          # name is required
    )
    email = db.Column(
        db.String(150),
        unique=True,            # no two users can share an email
        nullable=False
    )
    password = db.Column(
        db.String(255),         # long enough for bcrypt hash
        nullable=False
    )
    role = db.Column(
        db.String(20),
        default='customer'      # 'customer' or 'admin'
                                # default = 'customer' if not specified
    )

    # RELATIONSHIP: User → CartItem
    # One user can have many cart items.
    # backref='user' automatically adds a .user attribute
    # on CartItem, so cart_item.user gives the User object.
    # lazy=True means cart items are loaded only when accessed,
    # not on every User query (better performance).
    # cascade='all, delete-orphan' means if a User is deleted,
    # all their CartItems are automatically deleted too.

    cart_items = db.relationship(
        'CartItem',
        backref='user',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<User {self.email}>'


# BOOK TABLE
# Stores all books in the catalogue.

class Book(db.Model):

    __tablename__ = 'books'

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    title = db.Column(
        db.String(255),
        nullable=False
    )
    author = db.Column(
        db.String(255),
        nullable=False
    )
    price = db.Column(
        db.Numeric(10, 2),      # 10 digits total, 2 decimal places
        nullable=False
    )
    stock = db.Column(
        db.Integer,
        default=0               # how many copies are available
    )
    description = db.Column(
        db.Text,                # long text, no length limit
        nullable=True           # description is optional
    )
    cover = db.Column(
        db.String(255),
        default='#6c757d'     # image URL  → '/static/img/x.jpg' (later)
    )

    # RELATIONSHIP: Book → CartItem
    # One book can appear in many users' carts.
    # backref='book' automatically adds a .book attribute
    # on CartItem, so cart_item.book gives the Book object.
    # This is how cart/routes.py accesses item.book.title,
    # item.book.price, item.book.cover etc.
    # cascade='all, delete-orphan' means if a Book is deleted,
    # all CartItems referencing it are deleted too.

    cart_items = db.relationship(
        'CartItem',
        backref='book',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Book {self.title}>'


# CART ITEM TABLE
# Links a User to a Book with a quantity.
#
# NOTE: No relationships defined here.
# They are defined in User and Book above via backref=.
# This means:
#   cart_item.user → gives the User object (from User.backref)
#   cart_item.book → gives the Book object (from Book.backref)

class CartItem(db.Model):

    __tablename__ = 'cart_items'

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        # ondelete='CASCADE' → if user row is deleted in PostgreSQL,
        # their cart_items rows are deleted automatically at DB level.
        # The cascade in User relationship handles it at Python level.
        # Having both = doubly safe.
        nullable=False
    )
    book_id = db.Column(
        db.Integer,
        db.ForeignKey('books.id', ondelete='CASCADE'),
        # ondelete='CASCADE' → if a book is deleted from the DB,
        # all cart_items referencing that book are deleted too.
        nullable=False
    )
    quantity = db.Column(
        db.Integer,
        default=1               # default 1 copy when first added
    )

    def __repr__(self):
        return f'<CartItem user={self.user_id} book={self.book_id} qty={self.quantity}>'
