# app/cart/routes.py
# ─────────────────────────────────────────────────────────────
# PURPOSE: Handle all cart routes.
# /cart              → view cart (login required)
# /cart/add/<id>     → add book to cart (login required)
# /cart/remove/<id>  → remove item from cart (login required)
# /cart/update/<id>  → update quantity (login required)
# /cart/checkout     → checkout page (login required)
# /cart/payment      → process payment (login required)
# /cart/processing   → processing page (login required)
# /cart/order/confirmation → order confirmation (login required)
#
# ALL cart routes require login — cart is personal data.
# Stock is updated in real time:
#   add to cart     → stock decreases
#   remove from cart → stock increases
#   update quantity  → stock adjusts by difference
#   place order      → cart cleared (stock already updated)
# ─────────────────────────────────────────────────────────────


from flask import render_template, redirect, url_for, flash, Blueprint, request, session
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Book, CartItem
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# BLUEPRINT
# ─────────────────────────────────────────────────────────────
cart = Blueprint('cart', __name__)


# ─────────────────────────────────────────────────────────────
# VIEW CART
# Shows all items in the logged-in user's cart.
# Calculates total price.
# ─────────────────────────────────────────────────────────────
@cart.route('/cart')
@login_required
def view_cart():

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    total = sum(
        float(item.book.price) * item.quantity
        for item in cart_items
    )

    return render_template(
        'cart/cart.html',
        cart_items=cart_items,
        total=total
    )


# ─────────────────────────────────────────────────────────────
# ADD TO CART
# Adds a book to the cart or increases quantity if already
# in cart. Decreases book stock by 1 on each add.
# Always POST — never GET (modifies data).
# ─────────────────────────────────────────────────────────────
@cart.route('/cart/add/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):

    book = Book.query.get_or_404(book_id)

    # Block add if out of stock
    if book.stock <= 0:
        flash(f'Sorry, "{book.title}" is out of stock.', 'danger')
        return redirect(url_for('catalogue.books'))

    existing_item = CartItem.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()

    if existing_item:
        # Already in cart — increase quantity, decrease stock
        existing_item.quantity += 1
        book.stock -= 1
        flash(f'"{book.title}" quantity updated in your cart.', 'success')
    else:
        # Not in cart yet — create new item, decrease stock
        new_item = CartItem(
            user_id=current_user.id,
            book_id=book_id,
            quantity=1
        )
        db.session.add(new_item)
        book.stock -= 1
        flash(f'"{book.title}" added to your cart!', 'success')

    db.session.commit()

    return redirect(request.referrer or url_for('catalogue.books'))


# ─────────────────────────────────────────────────────────────
# REMOVE FROM CART
# Removes one cart item entirely regardless of quantity.
# Restores the full quantity back to book stock.
# Always POST — never GET (modifies data).
# ─────────────────────────────────────────────────────────────
@cart.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):

    item = CartItem.query.get_or_404(item_id)

    # Security check — item must belong to logged-in user
    if item.user_id != current_user.id:
        flash('You are not allowed to do that.', 'danger')
        return redirect(url_for('cart.view_cart'))

    book_title = item.book.title

    # Restore full quantity back to stock before deleting
    item.book.stock += item.quantity

    db.session.delete(item)
    db.session.commit()

    flash(f'"{book_title}" removed from your cart.', 'info')
    return redirect(url_for('cart.view_cart'))


# ─────────────────────────────────────────────────────────────
# UPDATE QUANTITY
# Changes the quantity of a specific cart item.
# Adjusts book stock by the difference between old and new qty.
#
# difference = new_quantity - old_quantity
#   positive → user increased qty → stock decreases
#   negative → user decreased qty → stock increases
#
# Always POST — never GET (modifies data).
# ─────────────────────────────────────────────────────────────
@cart.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_quantity(item_id):

    item = CartItem.query.get_or_404(item_id)

    # Security check
    if item.user_id != current_user.id:
        flash('You are not allowed to do that.', 'danger')
        return redirect(url_for('cart.view_cart'))

    new_quantity = int(request.form.get('quantity', 1))

    if new_quantity <= 0:
        # Quantity set to 0 — restore full stock and remove item
        item.book.stock += item.quantity
        db.session.delete(item)
        flash(f'"{item.book.title}" removed from your cart.', 'info')
    else:
        # Calculate how much stock to adjust
        # e.g. old=2, new=5 → difference=+3 → stock drops by 3
        # e.g. old=5, new=2 → difference=-3 → stock rises by 3
        difference = new_quantity - item.quantity

        # Guard: prevent taking more than available stock
        if difference > 0 and item.book.stock < difference:
            flash(
                f'Only {item.book.stock} more copy/copies of '
                f'"{item.book.title}" available.', 'warning'
            )
            return redirect(url_for('cart.view_cart'))

        item.book.stock -= difference
        item.quantity = new_quantity
        flash(f'Quantity updated for "{item.book.title}".', 'success')

    db.session.commit()
    return redirect(url_for('cart.view_cart'))


# ─────────────────────────────────────────────────────────────
# CHECKOUT
# Shows the checkout page with order summary.
# ─────────────────────────────────────────────────────────────
@cart.route('/cart/checkout')
@login_required
def checkout():

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash('Your cart is empty. Add some books first!', 'warning')
        return redirect(url_for('catalogue.books'))

    total = sum(
        float(item.book.price) * item.quantity
        for item in cart_items
    )

    return render_template(
        'cart/checkout.html',
        cart_items=cart_items,
        total=total
    )


# ─────────────────────────────────────────────────────────────
# PROCESS PAYMENT (POST)
# Triggered when user clicks "Place Order" on checkout page.
# Stock is already updated at add-to-cart time — no stock
# changes needed here.
# Clears cart, stores order summary in session, redirects to
# processing page. Uses POST-Redirect-GET pattern to prevent
# form resubmission on browser refresh.
# ─────────────────────────────────────────────────────────────
@cart.route('/cart/payment', methods=['POST'])
@login_required
def process_payment():

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('catalogue.books'))

    total = sum(float(item.book.price) * item.quantity for item in cart_items)

    # Build order summary for session — displayed on confirmation page
    order = {
        'order_id': f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{current_user.id}",
        'name':     current_user.name,
        'email':    current_user.email,
        'items': [
            {
                'title':    item.book.title,
                'author':   item.book.author,
                'quantity': item.quantity,
                'price':    float(item.book.price),
                'subtotal': round(float(item.book.price) * item.quantity, 2)
            }
            for item in cart_items
        ],
        'total': round(total, 2)
    }

    # Save order to session BEFORE clearing cart
    session['last_order'] = order

    # Clear the cart — stock was already decremented at add-to-cart
    for item in cart_items:
        db.session.delete(item)
    db.session.commit()

    return redirect(url_for('cart.processing'))


# ─────────────────────────────────────────────────────────────
# PROCESSING PAGE (GET)
# Shown after payment POST. Spinner auto-redirects to
# confirmation after 2.5 seconds via JavaScript.
# Blocked if accessed directly without a session order.
# ─────────────────────────────────────────────────────────────
@cart.route('/cart/processing')
@login_required
def processing():

    if 'last_order' not in session:
        flash('No active order found.', 'warning')
        return redirect(url_for('catalogue.books'))

    return render_template('cart/processing.html')


# ─────────────────────────────────────────────────────────────
# ORDER CONFIRMATION (GET)
# Pops order from session — one-time view only.
# Revisiting this URL after viewing redirects to catalogue.
# ─────────────────────────────────────────────────────────────
@cart.route('/cart/order/confirmation')
@login_required
def order_confirmation():

    order = session.pop('last_order', None)

    if not order:
        flash('No recent order found. Browse our books!', 'warning')
        return redirect(url_for('catalogue.books'))

    return render_template('cart/order_confirmation.html', order=order)
