import re
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from numpy import delete
from .models import User, Post
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
    return render_template('profile.html', name = current_user.name, bio = current_user.bio)

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


# Post related functions
# TODO: Complete once front end components are added
def create_post():
    print("post creation", request.form)
    # if request.form.get('action') == "Create Post":
    if request.form.get('action') == "Create Post":  
        text = "test post"
        contents = "test"
        topic_list = "topic1,topic2,topic3"
        new_post = Post(user_id=current_user.id, contents=contents, topic_list=topic_list)
        db.session.add(new_post)
        db.session.commit()
    # TODO: Display some sort of post creation message
    return redirect(url_for('main.profile'))


@login_required
def delete_post():
    post_id = 0 # set this to request form value
    if request.form.get('action') == "Delete Post":
        obj = Post.query.filter_by(id=post_id)
        db.session.delete(obj)
        db.session.commit()
    # TODO: Display some sort of post deletion message 
    return redirect(url_for('main.profile')) 


def get_urls(contents):
    url_list = re.findall(r'(https?://[^\s]+)', contents)
    return url_list
