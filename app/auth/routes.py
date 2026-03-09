#Purpose: Handles all authentication routes.
#signup -> create new account
#login -> verify credentials and start session
#logout -> end session and redirect to login
#
#blueprint: groups related routes together
# "auth" is blueprint name used in url for auth_login

from flask import render_template, redirect, url_for, flash, Blueprint, request, make_response
from flask_login import (login_user, logout_user, login_required, current_user)
from app.extensions import db, bcrypt
from app.models import User
from app.auth.forms import SignupForm, LoginForm
from flask import make_response 

#Blueprint groups related routes together, 
auth = Blueprint('auth', __name__)

#Signup route
#GET -> Show empty signup form
#POST -> Validate form data and create new user

@auth.route('/signup', methods=['GET', 'POST'])
def signup():

    #Redirects user to books page if authenticated
    if current_user.is_authenticated:
        return redirect(url_for('catalogue.books'))
    
    form = SignupForm

    #Checks request is POST AND all form validators passed
    if form.validate_on_submit():

        #Hashed plaintext password
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        #Creates new User object with form data
        new_user = User(
            name     = form.name.data,
            email    = form.email.data,
            password = hashed_pw        # store hashed, not plain
        )

        #add to database session
        db.session.add(new_user)

        #commit changes to PostgreSQL
        db.session.commit()

        #Flash one time message for success
        flash('Account created successfully! Please log in.', 'success')

        #Redirect to login page after successful signup
        return redirect(url_for('auth.login'))

    #If GET request OR form validation failed
    #Render signup template again and pass form object
    return render_template('auth/signup.html', form=form)

#Login route
#GET -> Show empty login form
#POST-> check credentials and log user in

@auth.route('/login', methods=['GET', 'POST'])
def login():

    #Same redirect as previously if user authenticated
    if current_user.is_authenticated:
        return redirect(url_for('catalogue.books'))
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        #Checks form information against database
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)

            #Flashes success message
            flash(f'Welcome back, {user.name}!', 'success')

            #If redirected to log in page from protected page
            #Sends user back to that page instead of to /books
            #Validate starts with / to prevent open redirect attacks
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            
            #Otherwise redirect normally
            return redirect(url_for('catalogue.books'))

        #Flash fail message if incorrect credentials
        flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html', form=form)

#Logout route
#Tagged with login required so only logged-in users can access the page
#If not logged in flask redirects to login page

@auth.route('/logout')
@login_required
def logout():

    #Clears user session from browser cookie
    logout_user()


    #Clears all cached pages, cookies and storage on logout
    #Results in redirect to login
    response = make_response(redirect(url_for('auth.login')))
    response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage"'


    return response