import re
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from numpy import delete
from .models import User, Post
from . import db
from werkzeug.security import generate_password_hash

prof = Blueprint('prof', __name__)

# Profile page
@prof.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name = current_user.name, bio = current_user.bio, id = current_user.id)

# Edit Profile Page
@prof.route('/edit_profile')
@login_required
def edit_profile():
    return render_template('edit_profile.html', name = current_user.name, bio = current_user.bio)

# Account delete and other functions, differentiated based on 'action's value
@prof.route('/profile', methods=['POST'])
@login_required
def profile_delete():
    # Deleting a user account and all of their associated data
    if request.form.get('action') == "Delete Account":
        obj = User.query.filter_by(id=current_user.id).one()
        db.session.delete(obj)
        db.session.commit()
        return redirect(url_for('auth.logout'))

    # TODO: Other buttons if they exist
    return redirect(url_for('prof.profile'))

# Access the Edit Profile page
@prof.route('/edit_profile', methods=['GET'])
@login_required
def show_edit_profile():
    return redirect(url_for('prof.edit_profile'))

# Functionality to update a user's profile
@prof.route('/edit_profile', methods=['POST'])
@login_required
def update_profile():
    if request.form.get('action') == "Edit Profile":

        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'), method='sha256')
        name = request.form.get('name')
        bio = request.form.get('bio')

        if not email:
            email = current_user.email
        if not password:
            password = current_user.password
        if not name:
            name = current_user.name
        if not bio:
            bio = current_user.bio

        user = User.query.filter_by(email=email).first() 
        user.email = email
        user.password = password
        user.name = name
        user.bio = bio 
        db.session.merge(user)
        db.session.flush()
        db.session.commit()
    return redirect(url_for('prof.profile'))

# View another user's profile
@prof.route('/view_profile/<id>')
def view_profile(id):
    user_to_view = User.query.get(id)
    return render_template('other_profile_view.html', name = user_to_view.name, bio = user_to_view.bio, id = user_to_view.id)

# Following another dude TEMP
@prof.route('/follow_user/<id>')
def follow_user(id):
    # id of user to be followed should be supplied by whatever is calling this
    #print(id)
    return redirect(url_for('prof.view_profile', id=id))
    # Following another dude TEMP

@prof.route('/unfollow_user/<id>')
def unfollow_user(id):
    # id of user to be unfollowed should be supplied by whatever is calling this
    #print(id)
    return redirect(url_for('prof.view_profile', id=id))