import re
from flask import Blueprint, redirect, render_template, request, url_for, flash, jsonify
from flask_login import login_required, current_user, UserMixin
from numpy import delete
import pusher
from .models import User, Post, Topic, Message
from .posts import post_to_html
from . import db
from werkzeug.security import generate_password_hash

prof = Blueprint('prof', __name__)

# Profile page
@prof.route('/profile')
@login_required
def profile():
    # TODO: post_to_html parameter is only for testing purposes, REMOVE 
    return render_template('profile.html', name = current_user.name, bio = current_user.bio, id = current_user.id, post_to_html=post_to_html)

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

# Function to turn a user into some html usable text
def user_to_html(user_id):
    user_to_view = User.query.get(user_id)

    # Grab and shorten bio if need be
    bio = user_to_view.bio
    if (isinstance(bio, type(None))):
        bio = "None"
    if (len(bio) > 20):
        bio = bio[0:20] + "..."
    # html conversion
    html_string =  "<div class=\"box\">\
                        <h3>Name: " + str(user_to_view.name) + "</h3>\
                        <h3>Bio: " + str(bio) + "</h3>\
                        <form action=\"/view_profile/" + str(user_id) + "\">\
                            <button>View this User</button>\
                        </form>\
                    </div>"
 
    return html_string


# Create a list of all the possible people a user could have been searching for
@prof.route('/search_user', methods=['GET'])
def search_user():
    # Grab what username was searched for, put list of possible users into possible_people
    username = request.args.get('search')
    possible_people = User.query.filter_by(name=username).all()
    print(possible_people)
    everyone_get_in_here = ""

    # Using list of possible users, turn all users into html strings with their id's
    for i in range(len(possible_people)):
        id_cur = possible_people[i].id
        print(id_cur)
        everyone_get_in_here += user_to_html(id_cur)

    # String will be empty if no possible users were found, add the error
    if (len(everyone_get_in_here) == 0):
        everyone_get_in_here += "<div class=\"box\">\
                                    <h3>No Users of that username were found!</h3>\
                                 </div>"
    return render_template('search_users.html', users_string = everyone_get_in_here)
    

# View another user's profile
@prof.route('/view_profile/<id>')
def view_profile(id):
    user_to_view = User.query.get(id)
    return render_template('other_profile_view.html', user = user_to_view, name = user_to_view.name, bio = user_to_view.bio, id = id, followed_topics = list(user_to_view.followed_topics))

# Following another dude
@prof.route('/follow_user/<id>')
def follow_user(id):
    # id of user to be followed should be supplied by whatever is calling this
    #print(id)
    user = User.query.filter_by(id=id).first()
    if current_user.is_following(user):
        flash('Hey buddy I know you like this guy, but you\'re already following them')
        return redirect(url_for('prof.view_profile', id=id))
    if user == current_user:
        flash('Hey dude u cant follow yourself, like ur not that cool')
        return redirect(url_for('prof.view_profile', id=id))
    current_user.follow(user)
    flash('You are following {}!'.format(user.name))
    db.session.commit()
    return redirect(url_for('prof.view_profile', id=id))

# Unfollowing another dude
@prof.route('/unfollow_user/<id>')
def unfollow_user(id):
    # id of user to be unfollowed should be supplied by whatever is calling this
    #print(id)
    user = User.query.filter_by(id=id).first()
    if user is None:
        return redirect(url_for('index', id=id))
    if user == current_user:
        return redirect(url_for('user', id=id))
    current_user.unfollow(user)
    db.session.commit()
    return redirect(url_for('prof.view_profile', id=id))

# View a topic
@prof.route('/view_topic/<id>')
def view_topic(id):
    topic_to_view = Topic.query.get(id)
    return render_template('topic.html', name = topic_to_view.name, id = id)

@prof.route('/follow_topic/<id>')
def follow_topic(id):
    topic = Topic.query.filter_by(id=id).first()
    if current_user.is_following_topic(topic):
        flash('topic is already followed')
        return redirect(url_for('prof.view_topic', id=id))
    current_user.follow_topic(topic)
    db.session.commit()
    return redirect(url_for('prof.view_topic', id=id))


# Chat server setup
pusher_client = pusher.Pusher(
app_id='1385712',
key='4eefb1b81ae21d331cbf',
secret='441266c2faec85226f05',
cluster='us2',
ssl=True
)

@prof.route('/chat_with/<id>')
def chat_with(id):

    user = User.query.filter_by(id=id).first()
    new_name = user.name

    # Can query only of the 2 id's that are chatting
    messages = Message.query.filter_by(username=current_user.name)
    messages2 = Message.query.filter_by(username=new_name)
    messages_total = messages.union(messages2)
    # messages_total = Message.query.all()
    #print(messages_total)
    #messages2 = Message.query.filter_by(username=new_name)

    return render_template('starting_template.html', messages=messages_total, curr_user=current_user, id=id)

@prof.route('/message', methods=['POST'])
def message():
    try:
        username = current_user.name
        message = request.form.get('message')
        db.create_all()
        new_message = Message(username=username, message=message)
        db.session.add(new_message)
        db.session.commit()

        pusher_client.trigger('chat-channel', 'new-message', {'username': username, 'message': message})
        return jsonify({'result' : 'success'})
    except:
        return jsonify({'result' : 'error'})

