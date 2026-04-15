# catalogue-service/app/models.py

from datetime import datetime
from .extensions import db


class Book(db.Model):
    __tablename__ = "books"

    id          = db.Column(db.Integer,     primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    author      = db.Column(db.String(200), nullable=False)
    price       = db.Column(db.Float,       nullable=False)
    stock       = db.Column(db.Integer,     nullable=False, default=0)
    description = db.Column(db.Text,        nullable=True)
    isbn        = db.Column(db.String(20),  nullable=True, unique=True)
    cover       = db.Column(db.String(20),  nullable=True)   # hex colour e.g. #e74c3c
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime,    default=datetime.utcnow,
                                            onupdate=datetime.utcnow)

    def to_dict(self):
        """Serialise Book to JSON-safe dict for API responses."""
        return {
            "id":          self.id,
            "title":       self.title,
            "author":      self.author,
            "price":       self.price,
            "stock":       self.stock,
            "description": self.description,
            "isbn":        self.isbn,
            "cover":       self.cover,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
            "updated_at":  self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Book {self.id} — {self.title}>"
