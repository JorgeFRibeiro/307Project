from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from .models import User
from . import db

main = Blueprint('main', __name__)

# Home/index page
@main.route('/')
def index():
    return render_template('index.html')

# Profile page
@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name = current_user.name)

# Account delete and other functions, differentiated based on 'action's value
@main.route('/profile', methods=['POST'])
@login_required
def profile_delete():
    # Deleting a user account and all of their associated data
    if request.form.get('action') == "Delete Account":
        obj = User.query.filter_by(id=current_user.id).one()
        db.session.delete(obj)
        db.session.commit()
        return redirect(url_for('auth.logout'))

    # TODO: Other buttons if they exist
    return redirect(url_for('main.profile'))