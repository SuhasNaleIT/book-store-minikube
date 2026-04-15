# app-service/app/models.py

from datetime import datetime
from flask_login import UserMixin
from .extensions import db, login_manager, bcrypt


# ── User loader required by Flask-Login ───────────────────────
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship("Order", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Order(db.Model):
    __tablename__ = "orders"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total_price = db.Column(db.Float,   nullable=False)
    status      = db.Column(db.String(20), default="pending")  # pending | paid | cancelled
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy=True)

    def __repr__(self):
        return f"<Order {self.id} — User {self.user_id} — {self.status}>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id                = db.Column(db.Integer, primary_key=True)
    order_id          = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)

    # ⚠️  book_id is a plain Integer — NOT a ForeignKey
    # Books live in catalogue-service's own DB.
    # We store the ID only as a reference, no DB-level constraint.
    book_id           = db.Column(db.Integer, nullable=False)

    quantity          = db.Column(db.Integer, nullable=False, default=1)

    # Snapshot of price at time of purchase — important because
    # catalogue-service prices can change after the order is placed.
    price_at_purchase = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<OrderItem book_id={self.book_id} qty={self.quantity}>"
