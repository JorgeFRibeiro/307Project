from flask import Blueprint, render_template
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

# Home/index page
@main.route('/')
def index():
    return render_template('index.html')

# Profile page
@main.route('/profile')
@login_required
def profile():

    # TODO: replace passed info about current user with actual needed info
    return render_template('profile.html', name = current_user.name)