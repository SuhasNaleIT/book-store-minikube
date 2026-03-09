#Purpose: Define login and signup forms with validation rules
#Flask-WTF handles CSRF protection
#WTForms handles field validation

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (DataRequired, Email, Length, EqualTo, ValidationError)
from app.models import User

#Signup form
#Used on Signup form
#Validates all fields before creating account

class SignupForm(FlaskForm):

    name = StringField(
        'Full Name', # label shown on HTML form
        validators=[
            DataRequired(),# field cannot be empty
            Length(min=2, max=100, message='Name must be between 2 and 100 characters')
        ]
    )
    
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(), # field cannot be empty
            Email(message='Please enter a valid email address') # checks format: x@x.x
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6, message='Password must be at least 6 characters')
        ]
    )

    confirm = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match') # must match password field
        ]
    )

    submit = SubmitField('Create Account')  # submit button label

    #Custom validator to check against db for matching email

    def validate_email(self, email):
        # query PostgreSQL via SQLAlchemy to find existing user
        user = User.query.filter_by(email=email.data).first()
        if user:
            # raising ValidationError shows this message
            # on the form next to the email field
            raise ValidationError(
                'Email already registered. Please login instead.'
            )
        
#Login form
#Used on login page
#Emails validated in routes.py (As to not reveal which emails registered)
class LoginForm(FlaskForm):

    email = StringField(
        'Email Address',
        validators=[
            DataRequired(),
            Email(message='Please enter a valid email address')
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField('Login')
