# app-service/tests/test_cart.py

import pytest
from unittest.mock import patch, MagicMock
from app.models import Order, OrderItem


# ─────────────────────────────────────────────────────────────
# VIEW CART TESTS
# ─────────────────────────────────────────────────────────────
class TestViewCart:

    def test_cart_requires_login(self, client):
        resp = client.get("/cart", follow_redirects=True)
        assert b"Please log in" in resp.data

    def test_empty_cart_loads(self, logged_in_client):
        resp = logged_in_client.get("/cart")
        assert resp.status_code == 200
        assert b"cart" in resp.data.lower()

    def test_cart_shows_items(
        self, logged_in_client, mock_catalogue_single_book
    ):
        # Seed session cart with one item
        with logged_in_client.session_transaction() as sess:
            sess["cart"] = {"1": 2}

        resp = logged_in_client.get("/cart")
        assert resp.status_code == 200
        assert b"The Great Gatsby" in resp.data


# ─────────────────────────────────────────────────────────────
# ADD TO CART TESTS
# ─────────────────────────────────────────────────────────────
class TestAddToCart:

    def test_add_requires_login(self, client):
        resp = client.post("/cart/add/1", follow_redirects=True)
        assert b"Please log in" in resp.data

    def test_add_book_to_cart(
        self, logged_in_client, mock_catalogue_single_book
    ):
        resp = logged_in_client.post(
            "/cart/add/1", follow_redirects=True
        )
        assert resp.status_code == 200
        assert b"added to your cart" in resp.data

        with logged_in_client.session_transaction() as sess:
            assert "1" in sess["cart"]
            assert sess["cart"]["1"] == 1

    def test_add_same_book_increments_quantity(
        self, logged_in_client, mock_catalogue_single_book
    ):
        with logged_in_client.session_transaction() as sess:
            sess["cart"] = {"1": 1}

        logged_in_client.post("/cart/add/1", follow_redirects=True)

        with logged_in_client.session_transaction() as sess:
            assert sess["cart"]["1"] == 2

    def test_add_out_of_stock_book(self, logged_in_client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": 1, "title": "Old Book",
            "price": 9.99, "stock": 0
        }
        with patch("requests.get", return_value=mock_resp):
            resp = logged_in_client.post(
                "/cart/add/1", follow_redirects=True
            )
        assert b"out of stock" in resp.data

    def test_add_when_catalogue_unavailable(self, logged_in_client):
        with patch(
            "requests.get",
            side_effect=Exception("Connection refused")
        ):
            resp = logged_in_client.post(
                "/cart/add/1", follow_redirects=True
            )
        assert b"unavailable" in resp.data


# ─────────────────────────────────────────────────────────────
# REMOVE FROM CART TESTS
# ─────────────────────────────────────────────────────────────
class TestRemoveFromCart:

    def test_remove_requires_login(self, client):
        resp = client.post("/cart/remove/1", follow_redirects=True)
        assert b"Please log in" in resp.data

    def test_remove_item_from_cart(self, logged_in_client):
        with logged_in_client.session_transaction() as sess:
            sess["cart"] = {"1": 2, "2": 1}

        resp = logged_in_client.post(
            "/cart/remove/1", follow_redirects=True
        )
        assert resp.status_code == 200
        assert b"removed from cart" in resp.data

        with logged_in_client.session_transaction() as sess:
            assert "1" not in sess["cart"]
            assert "2" in sess["cart"]


# ─────────────────────────────────────────────────────────────
# UPDATE QUANTITY TESTS
# ─────────────────────────────────────────────────────────────
class TestUpdateQuantity:

    def test_update_requires_login(self, client):
        resp = client.post(
            "/cart/update/1", data={"quantity": 3},
            follow_redirects=True
        )
        assert b"Please log in" in resp.data

    def test_update_quantity_success(
        self, logged_in_client, mock_catalogue_single_book
    ):
        with logged_in_client.session_transaction() as sess:
            sess["cart"] = {"1": 1}

        resp = logged_in_client.post(
            "/cart/update/1",
            data={"quantity": 3},
            follow_redirects=True
        )
        assert resp.status_code == 200

        with logged_in_client.session_transaction() as sess:
            assert sess["cart"]["1"] == 3

    def test_update_quantity_to_zero_removes_item(
        self, logged_in_client
    ):
        with logged_in_client.session_transaction() as sess:
            sess["cart"] = {"1": 2}

        resp = logged_in_client.post(
            "/cart/update/1",
            data={"quantity": 0},
            follow_redirects=True
        )
        assert resp.status_code == 200

        with logged_in_client.session_transaction() as sess:
            assert "1" not in sess.get("cart", {})

    def test_update_quantity_exceeds_stock(self, logged_in_client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": 1, "title": "The Great Gatsby",
            "price": 9.99, "stock": 3
        }
        with logged_in_client.session_transaction() as sess:
            sess["cart"] = {"1": 1}

        with patch("requests.get", return_value=mock_resp):
            resp = logged_in_client.post(
                "/cart/update/1",
                data={"quantity": 10},  # exceeds stock of 3
                follow_redirects=True
            )
        assert b"available" in resp.data


# ─────────────────────────────────────────────────────────────
# CHECKOUT PAGE TESTS
# ─────────────────────────────────────────────────────────────
class TestCheckoutPage:

    def test_checkout_requires_login(self, client):
        resp = client.get("/cart/checkout", follow_redirects=True)
        assert b"Please log in" in resp.data

    def test_checkout_empty_cart_redirects(self, logged_in_client):
        with logged_in_client.session_transaction() as sess:
            sess["cart"] = {}

        resp = logged_in_client.get(
            "/cart/checkout", follow_redirects=True
        )
        assert b"empty" in resp.data

    def test_checkout_page_loads_with_items(
        self, logged_in_client, mock_catalogue_single_book
    ):
        with logged_in_client.session_transaction() as sess:
            sess["cart"] = {"1": 2}

        resp = logged_in_client.get("/cart/checkout")
        assert resp.status_code == 200
        assert b"The Great Gatsby" in resp.data


# ─────────────────────────────────────────────────────────────
# PROCESS PAYMENT TESTS
# ─────────────────────────────────────────────────────────────
class TestProcessPayment:

    def test_payment_requires_login(self, client):
        resp = client.post("/cart/payment", follow_redirects=True)
        assert b"Please log in" in resp.data

    def test_payment_success_creates_order(
        self,
        logged_in_client,
        db,
        mock_catalogue_single_book,
        mock_stock_patch_success
    ):
        with logged_in_client.session_transaction() as sess:
            sess["cart"] = {"1": 1}

        resp = logged_in_client.post(
            "/cart/payment", follow_redirects=True
        )
        assert resp.status_code == 200

        # Order written to DB
        from flask import current_app
        order = Order.query.first()
        assert order is not None
        assert order.status == "paid"
        assert order.total_price == 9.99

        # OrderItem written to DB
        item = OrderItem.query.filter_by(order_id=order.id).first()
        assert item is not None
        assert item.book_id == 1
        assert item.price_at_purchase == 9.99

    def test_payment_clears_cart(
        self,
        logged_in_client,
        mock_catalogue_single_book,
        mock_stock_patch_success
    ):
        with logged_in_client.session_transaction() as sess:
            sess["cart"] = {"1": 1}

        logged_in_client.post("/cart/payment", follow_redirects=True)

        with logged_in_client.session_transaction() as sess:
            assert sess.get("cart") == {}

    def test_payment_empty_cart_redirects(self, logged_in_client):
        with logged_in_client.session_transaction() as sess:
            sess["cart"] = {}

        resp = logged_in_client.post(
            "/cart/payment", follow_redirects=True
        )
        assert b"empty" in resp.data

    def test_payment_catalogue_unavailable_rolls_back(
        self, logged_in_client, db
    ):
        with logged_in_client.session_transaction() as sess:
            sess["cart"] = {"1": 1}

        with patch(
            "requests.get",
            side_effect=Exception("Connection refused")
        ):
            resp = logged_in_client.post(
                "/cart/payment", follow_redirects=True
            )

        assert b"unavailable" in resp.data
        assert Order.query.count() == 0  # rolled back ✅

    def test_payment_stock_patch_fails_rolls_back(
        self,
        logged_in_client,
        db,
        mock_catalogue_single_book,
        mock_stock_patch_fail
    ):
        with logged_in_client.session_transaction() as sess:
            sess["cart"] = {"1": 1}

        resp = logged_in_client.post(
            "/cart/payment", follow_redirects=True
        )
        assert b"Stock update failed" in resp.data
        assert Order.query.count() == 0  # rolled back ✅


# ─────────────────────────────────────────────────────────────
# ORDER HISTORY TESTS
# ─────────────────────────────────────────────────────────────
class TestOrderHistory:

    def test_order_history_requires_login(self, client):
        resp = client.get("/orders", follow_redirects=True)
        assert b"Please log in" in resp.data

    def test_order_history_shows_orders(
        self, logged_in_client, test_order
    ):
        resp = logged_in_client.get("/orders")
        assert resp.status_code == 200
        assert b"paid" in resp.data
