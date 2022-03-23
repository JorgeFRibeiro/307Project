import re
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from .models import User, Post
from . import db
from werkzeug.security import generate_password_hash

posts = Blueprint('posts', __name__)


# Post related functions
@posts.route('/create_post', methods=['POST'])
def create_post():
    print("post creation", request.form)
    if request.form.get('action') == "Create Post":
        text = "test post"
        contents = "test"
        topic_list = "topic1,topic2,topic3"
        new_post = Post(user_id=current_user.id,
                        contents=contents, topic_list=topic_list)
        db.session.add(new_post)
        db.session.commit()
    # TODO: Display some sort of post creation message
    return redirect(url_for('prof.profile'))
    
@posts.route('/delete_post', methods=['POST'])
@login_required
def delete_post():
    post_id = 3 # set this to request form value
    print("deleting post: ", post_id)
    if request.form.get('action') == "Delete Post":
        obj = Post.query.filter_by(id=post_id).one()
        db.session.delete(obj)
        db.session.commit()
    # TODO: Display some sort of post deletion message 
    return redirect(url_for('prof.profile')) 


#Temporary gateway to view posts temporary display NOT FINAL
@posts.route('/view_temp', methods=['POST'])
@login_required
def view_temp():
    return render_template('posttemp.html')


def get_urls(contents):
    url_list = re.findall(r'(https?://[^\s]+)', contents)
    return url_list