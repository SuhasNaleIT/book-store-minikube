import random
import json

# Your actual seeded books from catalogue-service
BOOKS = [
    {
        "title": "1984",
        "author": "George Orwell",
        "price": 7.99,
        "isbn": "978-0451524935",
        "description": "A dystopian novel set in a totalitarian society ruled by Big Brother."
    },
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "price": 9.99,
        "isbn": "978-0743273565",
        "description": "A tale of wealth, obsession and the American Dream set in the Jazz Age."
    },
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "price": 8.99,
        "isbn": "978-0061935466",
        "description": "A powerful story of racial injustice and moral growth in the American South."
    },
    {
        "title": "Brave New World",
        "author": "Aldous Huxley",
        "price": 6.99,
        "isbn": "978-0060850524",
        "description": "A chilling vision of a future society where humans are engineered and conditioned."
    },
    {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "price": 11.99,
        "isbn": "978-0261102217",
        "description": "The beloved fantasy adventure of Bilbo Baggins on an unexpected journey."
    },
    {
        "title": "Dune",
        "author": "Frank Herbert",
        "price": 11.99,
        "isbn": "978-0441013593",
        "description": "An epic science fiction saga set on the desert planet Arrakis."
    },
]

def handle(event, context):
    book = random.choice(BOOKS)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "recommendation": book,
            "source": "openfaas-serverless"
        })
    }