import re
import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash

from token import *
from email import *
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from . import db

auth = Blueprint('auth', __name__)

# Login page
@auth.route('/login')
def login():
    return render_template('login.html')
    

@auth.route('/login', methods=['POST'])
def login_post():
    # Grab information User passed to login fields
    email = request.form.get('email')
    password = request.form.get('password')
    remember = False
    if request.form.get('remember'):
        remember = True

    # Ensure that all the fields are filled in
    user = User.query.filter_by(email=email).first()
    if not email or not password:
        flash('PLEASE FILL OUT ALL DAH FIELDS')
        return redirect(url_for('auth.login'))
    
    # If the user is not in the database or login info is incorrect
    if not user or not check_password_hash(user.password, password): 
        flash('Login credentials were incorrect or User does not exist.')
        return redirect(url_for('auth.login'))

    # TODO: user must be set after verifying it is a valid user from database
    login_user(user, remember=remember)

    # Good2go login and send user to profile
    return redirect(url_for('main.profile'))


# TODO: Continue as Guest functionality for the login page


# Signup page
@auth.route('/signup')
def signup():
    return render_template('signup.html')

# Signup function
@auth.route('/signup', methods=['GET', 'POST'])
def signup_post():
    # Grab all the information User passed to Signup fields
    # TODO: Change with information actually to be used, doing so will
    #       require an update to signup.html as well as login.html
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first() 
        if not email or not name or not password:
            flash('PLEASE FILL OUT ALL DAH FIELDS')
            return redirect(url_for('auth.signup'))

        if user: # If the user do already be in the database, go back
            flash('YOU ALREADY EXIST GET OUTTA HERE BUDDY')
            return redirect(url_for('auth.signup'))

        # Create a new User with passed information
        # TODO: Create User with passed information into database
        new_dude = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), confirmed=False)
        print("HELLO HELLO HELLO")

        # TODO: Add new guy to database
        db.session.add(new_dude)
        db.session.commit()

        token = generate_confirmation_token(new_dude.email)
        confirm_url = url_for('new_dude.confirm_email', token=token, _external=True)
        html = render_template('templates/activate.html', confirm_url=confirm_url)
        subject = "Please confirm your email homie"
        send_email(new_dude.email, subject, html)

        login_user(new_dude)
        flash('A confirmation email has been sent via email.', 'success')
        return redirect(url_for("main.home"))
    return render_template('user/register.html', form=form)
    # Send user back to login page
    # return redirect(url_for('auth.login'))
    

# Logout function
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# E-Mail authentication
@auth.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('main.home'))