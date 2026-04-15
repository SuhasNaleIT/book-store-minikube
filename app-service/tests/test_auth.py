# app-service/tests/test_auth.py

import pytest
from app.models import User


# ─────────────────────────────────────────────────────────────
# REGISTRATION TESTS
# ─────────────────────────────────────────────────────────────
class TestRegistration:

    def test_register_page_loads(self, client):
        resp = client.get("/register")
        assert resp.status_code == 200
        assert b"Register" in resp.data

    def test_register_success(self, client, db):
        resp = client.post("/register", data={
            "username":         "newuser",
            "email":            "new@example.com",
            "password":         "password123",
            "confirm_password": "password123"
        }, follow_redirects=True)

        assert resp.status_code == 200
        assert b"Account created" in resp.data

        user = User.query.filter_by(email="new@example.com").first()
        assert user is not None
        assert user.username == "newuser"

    def test_register_duplicate_email(self, client, test_user):
        resp = client.post("/register", data={
            "username":         "anotheruser",
            "email":            "test@example.com",   # already exists
            "password":         "password123",
            "confirm_password": "password123"
        }, follow_redirects=True)

        assert resp.status_code == 200
        assert b"Email already registered" in resp.data

    def test_register_duplicate_username(self, client, test_user):
        resp = client.post("/register", data={
            "username":         "testuser",            # already exists
            "email":            "unique@example.com",
            "password":         "password123",
            "confirm_password": "password123"
        }, follow_redirects=True)

        assert resp.status_code == 200
        assert b"Username already taken" in resp.data

    def test_register_password_mismatch(self, client):
        resp = client.post("/register", data={
            "username":         "mismatchuser",
            "email":            "mismatch@example.com",
            "password":         "password123",
            "confirm_password": "wrongpassword"
        }, follow_redirects=True)

        assert resp.status_code == 200
        assert b"Passwords must match" in resp.data

    def test_register_short_password(self, client):
        resp = client.post("/register", data={
            "username":         "shortpass",
            "email":            "short@example.com",
            "password":         "abc",
            "confirm_password": "abc"
        }, follow_redirects=True)

        assert resp.status_code == 200
        assert b"at least 6 characters" in resp.data

    def test_register_invalid_email(self, client):
        resp = client.post("/register", data={
            "username":         "bademail",
            "email":            "not-an-email",
            "password":         "password123",
            "confirm_password": "password123"
        }, follow_redirects=True)

        assert resp.status_code == 200
        assert b"valid email" in resp.data


# ─────────────────────────────────────────────────────────────
# LOGIN TESTS
# ─────────────────────────────────────────────────────────────
class TestLogin:

    def test_login_page_loads(self, client):
        resp = client.get("/login")
        assert resp.status_code == 200
        assert b"Login" in resp.data

    def test_login_success(self, client, test_user):
        resp = client.post("/login", data={
            "email":    "test@example.com",
            "password": "password123"
        }, follow_redirects=True)

        assert resp.status_code == 200
        assert b"Welcome back" in resp.data

    def test_login_wrong_password(self, client, test_user):
        resp = client.post("/login", data={
            "email":    "test@example.com",
            "password": "wrongpassword"
        }, follow_redirects=True)

        assert resp.status_code == 200
        assert b"Invalid email or password" in resp.data

    def test_login_wrong_email(self, client):
        resp = client.post("/login", data={
            "email":    "nobody@example.com",
            "password": "password123"
        }, follow_redirects=True)

        assert resp.status_code == 200
        assert b"Invalid email or password" in resp.data

    def test_login_redirects_if_already_authenticated(
        self, logged_in_client
    ):
        resp = logged_in_client.get("/login", follow_redirects=True)
        assert resp.status_code == 200
        # Already logged in → redirected to home, not login page
        assert b"Login" not in resp.data


# ─────────────────────────────────────────────────────────────
# LOGOUT TESTS
# ─────────────────────────────────────────────────────────────
class TestLogout:

    def test_logout_success(self, logged_in_client):
        resp = logged_in_client.get("/logout", follow_redirects=True)
        assert resp.status_code == 200
        assert b"logged out" in resp.data

    def test_logout_requires_login(self, client):
        resp = client.get("/logout", follow_redirects=True)
        # Unauthenticated → redirected to login page
        assert b"Please log in" in resp.data


# ─────────────────────────────────────────────────────────────
# PROFILE TESTS
# ─────────────────────────────────────────────────────────────
class TestProfile:

    def test_profile_requires_login(self, client):
        resp = client.get("/profile", follow_redirects=True)
        assert b"Please log in" in resp.data

    def test_profile_loads_when_logged_in(self, logged_in_client):
        resp = logged_in_client.get("/profile")
        assert resp.status_code == 200
        assert b"testuser" in resp.data
