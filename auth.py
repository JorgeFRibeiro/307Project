import re
from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import User
from flask_login import login_user, login_required, logout_user, current_user

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

    if not email or not password:
        flash('PLEASE FILL OUT ALL DAH FIELDS')
        return redirect(url_for('auth.login'))
    
    good_login = True
    # TODO: Login verification, use boolean var good_login

    if not good_login: # User not in database or incorrect login info
        flash('Login credentials were incorrect or User does not exist.')
        return redirect(url_for('auth.login'))

    # TODO: user must be set after verifying it is a valid user from database
    user = User()
    login_user(user, remember = remember)

    # Good2go login and send user to profile
    #login_user(user, remember = remember)
    return redirect(url_for('main.profile'))


# TODO: Continue as Guest functionality for the login page


# Signup page
@auth.route('/signup')
def signup():
    return render_template('signup.html')

# Signup function
@auth.route('/signup', methods=['POST'])
def signup_post():
    he_do_exist = True

    # Grab all the information User passed to Signup fields
    # TODO: Change with information actually to be used, doing so will
    #       require an update to signup.html as well as login.html
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    if not email or not name or not password:
        flash('PLEASE FILL OUT ALL DAH FIELDS')
        return redirect(url_for('auth.signup'))

    # TODO: Password hashing for security

    
    # TODO: Validate new user. Use above bool var, he_do_exist
   

    if he_do_exist: # If the user do already be in the database, go back
        flash('YOU ALREADY EXIST GET OUTTA HERE BUDDY')
        return redirect(url_for('auth.signup'))

    # Create a new User with passed information
    # TODO: Create User with passed information into database
    new_dude = User()
    print("HELLO HELLO HELLO")

    # TODO: Add new guy to database

    # Send user back to login page
    return redirect(url_for('auth.login'))

# Logout function
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))