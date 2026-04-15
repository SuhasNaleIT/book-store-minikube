# app-service/app/cart/routes.py

import requests
from datetime import datetime
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, session, request, current_app
)
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Order, OrderItem

cart = Blueprint("cart", __name__)


# ── Helper: get catalogue-service base URL ────────────────────
def catalogue_url():
    return current_app.config["CATALOGUE_SERVICE_URL"]


# ── Helper: fetch a single book from catalogue-service ────────
def get_book(book_id):
    try:
        resp = requests.get(
            f"{catalogue_url()}/api/books/{book_id}",
            timeout=5
        )
        if resp.status_code == 200:
            return resp.json()
    except requests.exceptions.RequestException:
        pass
    return None


# ─────────────────────────────────────────────────────────────
# VIEW CART
# ─────────────────────────────────────────────────────────────
@cart.route("/cart")
@login_required
def view_cart():
    cart_items = []
    total      = 0.0
    cart_data  = session.get("cart", {})  # {book_id_str: quantity}

    for book_id_str, quantity in cart_data.items():
        book = get_book(book_id_str)
        if book:
            subtotal = book["price"] * quantity
            total   += subtotal
            cart_items.append({
                "book":     book,
                "quantity": quantity,
                "subtotal": round(subtotal, 2)
            })

    return render_template(
        "cart/cart.html",
        cart_items=cart_items,
        total=round(total, 2)
    )


# ─────────────────────────────────────────────────────────────
# ADD TO CART
# Stock is NOT decremented here — only at checkout.
# ─────────────────────────────────────────────────────────────
@cart.route("/cart/add/<int:book_id>", methods=["POST"])
@login_required
def add_to_cart(book_id):
    book = get_book(book_id)
    if not book:
        flash("Book not found or catalogue service unavailable.", "danger")
        return redirect(url_for("main.home"))

    if book.get("stock", 0) < 1:
        flash(f'"{book["title"]}" is out of stock.', "warning")
        return redirect(url_for("main.home"))

    cart_data       = session.get("cart", {})
    key             = str(book_id)
    cart_data[key]  = cart_data.get(key, 0) + 1
    session["cart"] = cart_data
    session.modified = True

    flash(f'"{book["title"]}" added to your cart!', "success")
    return redirect(request.referrer or url_for("main.home"))


# ─────────────────────────────────────────────────────────────
# REMOVE FROM CART
# ─────────────────────────────────────────────────────────────
@cart.route("/cart/remove/<int:book_id>", methods=["POST"])
@login_required
def remove_from_cart(book_id):
    cart_data = session.get("cart", {})
    cart_data.pop(str(book_id), None)
    session["cart"]  = cart_data
    session.modified = True
    flash("Item removed from cart.", "info")
    return redirect(url_for("cart.view_cart"))


# ─────────────────────────────────────────────────────────────
# UPDATE QUANTITY
# Validates against current live stock from catalogue-service.
# ─────────────────────────────────────────────────────────────
@cart.route("/cart/update/<int:book_id>", methods=["POST"])
@login_required
def update_quantity(book_id):
    new_quantity = int(request.form.get("quantity", 1))
    cart_data    = session.get("cart", {})
    key          = str(book_id)

    if new_quantity <= 0:
        cart_data.pop(key, None)
        flash("Item removed from cart.", "info")
    else:
        book = get_book(book_id)
        if not book:
            flash("Could not verify stock. Please try again.", "danger")
            return redirect(url_for("cart.view_cart"))

        if new_quantity > book.get("stock", 0):
            flash(
                f'Only {book["stock"]} copy/copies of '
                f'"{book["title"]}" available.', "warning"
            )
            return redirect(url_for("cart.view_cart"))

        cart_data[key] = new_quantity
        flash(f'Quantity updated for "{book["title"]}".', "success")

    session["cart"]  = cart_data
    session.modified = True
    return redirect(url_for("cart.view_cart"))


# ─────────────────────────────────────────────────────────────
# CHECKOUT PAGE (GET)
# Shows order summary before payment.
# ─────────────────────────────────────────────────────────────
@cart.route("/cart/checkout")
@login_required
def checkout():
    cart_data = session.get("cart", {})

    if not cart_data:
        flash("Your cart is empty. Add some books first!", "warning")
        return redirect(url_for("main.home"))

    cart_items = []
    total      = 0.0

    for book_id_str, quantity in cart_data.items():
        book = get_book(book_id_str)
        if book:
            subtotal = book["price"] * quantity
            total   += subtotal
            cart_items.append({
                "book":     book,
                "quantity": quantity,
                "subtotal": round(subtotal, 2)
            })

    return render_template(
        "cart/checkout.html",
        cart_items=cart_items,
        total=round(total, 2)
    )


# ─────────────────────────────────────────────────────────────
# PROCESS PAYMENT (POST)
# Triggered when user clicks "Place Order" on checkout page.
# 1. Re-validates stock from catalogue-service
# 2. Writes Order + OrderItems to app_db
# 3. Decrements stock in catalogue-service
# 4. Saves order summary to session for confirmation page
# 5. Clears cart → redirects to processing page
# POST-Redirect-GET pattern prevents form resubmission.
# ─────────────────────────────────────────────────────────────
@cart.route("/cart/payment", methods=["POST"])
@login_required
def process_payment():
    cart_data = session.get("cart", {})

    if not cart_data:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("main.home"))

    total       = 0.0
    order_items = []

    # ── Step 1: Validate stock + snapshot prices ──────────────
    for book_id_str, quantity in cart_data.items():
        book = get_book(book_id_str)

        if not book:
            flash("Catalogue service unavailable. Please try again.", "danger")
            return redirect(url_for("cart.view_cart"))

        if book.get("stock", 0) < quantity:
            flash(
                f'Not enough stock for "{book["title"]}". '
                f'Only {book["stock"]} left.', "warning"
            )
            return redirect(url_for("cart.view_cart"))

        subtotal = book["price"] * quantity
        total   += subtotal
        order_items.append({
            "book_id":           int(book_id_str),
            "title":             book["title"],
            "author":            book["author"],
            "quantity":          quantity,
            "price_at_purchase": book["price"],
            "price":             book["price"],
            "subtotal":          round(subtotal, 2)
        })

    # ── Step 2: Write Order + OrderItems to app_db ────────────
    order = Order(
        user_id     = current_user.id,
        total_price = round(total, 2),
        status      = "pending"
    )
    db.session.add(order)
    db.session.flush()  # get order.id before commit

    for item in order_items:
        db.session.add(OrderItem(
            order_id          = order.id,
            book_id           = item["book_id"],
            quantity          = item["quantity"],
            price_at_purchase = item["price_at_purchase"]
        ))

    # ── Step 3: Decrement stock in catalogue-service ──────────
    for item in order_items:
        try:
            resp = requests.patch(
                f"{catalogue_url()}/api/books/{item['book_id']}/stock",
                json={"quantity": item["quantity"]},
                timeout=5
            )
            if resp.status_code != 200:
                db.session.rollback()
                flash("Stock update failed. Please try again.", "danger")
                return redirect(url_for("cart.view_cart"))

        except requests.exceptions.RequestException:
            db.session.rollback()
            flash("Catalogue service unavailable. Please try again.", "danger")
            return redirect(url_for("cart.view_cart"))

    # ── Step 4: Finalise order ────────────────────────────────
    order.status = "paid"
    db.session.commit()

    # ── Step 5: Save order summary to session for confirmation
    session["last_order"] = {
        "order_id": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{current_user.id}",
        "name":     current_user.username,
        "email":    current_user.email,
        "items":    order_items,
        "total":    round(total, 2)
    }

    # ── Step 6: Clear cart ────────────────────────────────────
    session["cart"]  = {}
    session.modified = True

    return redirect(url_for("cart.processing"))


# ─────────────────────────────────────────────────────────────
# PROCESSING PAGE (GET)
# Spinner page — JS auto-redirects to confirmation after 2.5s.
# Blocked if accessed directly without a session order.
# ─────────────────────────────────────────────────────────────
@cart.route("/cart/processing")
@login_required
def processing():
    if "last_order" not in session:
        flash("No active order found.", "warning")
        return redirect(url_for("main.home"))

    return render_template("cart/processing.html")


# ─────────────────────────────────────────────────────────────
# ORDER CONFIRMATION (GET)
# Pops order from session — one-time view only.
# Revisiting after viewing redirects to home.
# ─────────────────────────────────────────────────────────────
@cart.route("/cart/order/confirmation")
@login_required
def order_confirmation():
    order = session.pop("last_order", None)

    if not order:
        flash("No recent order found. Browse our books!", "warning")
        return redirect(url_for("main.home"))

    return render_template("cart/order_confirmation.html", order=order)


# ─────────────────────────────────────────────────────────────
# ORDER HISTORY (GET)
# Reads from app_db — no catalogue-service call needed.
# Prices already snapshotted in order_items.price_at_purchase.
# ─────────────────────────────────────────────────────────────
@cart.route("/orders")
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id)\
                        .order_by(Order.created_at.desc()).all()
    return render_template("cart/orders.html", orders=orders)
