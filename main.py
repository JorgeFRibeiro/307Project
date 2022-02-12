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
@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Deleting a user account and all of their associated data
        if request.form.get('action1') == "Delete Account":
            obj = User.query.filter_by(id=current_user.id).one()
            db.session.delete(obj)
            db.session.commit()
            return redirect(url_for('auth.logout'))

    # TODO: replace passed info about current user with actual needed info
    return render_template('profile.html', name = current_user.name)