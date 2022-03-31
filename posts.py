import re
from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import login_required, current_user
from .models import User, Post, Topic
from . import db
from werkzeug.security import generate_password_hash

posts = Blueprint('posts', __name__)

NULL = 0

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

#Temporary function to get html to display a post
#TODO in profile.html in the Posts column, there is a placeholder call to this function
# in profile.py under the profile() function, you can find where the function is linked to the html
def post_to_html(post_id):
    #Currently done as <h3> because that is what lines up with in where the 
    #Post html is placed in timeline.html
    obj = Post.query.get(post_id)
    user_for_post = User.query.get(obj.user_id)
    contents = obj.contents
    topics = obj.topic_list.split(',')
    username = user_for_post.name
    
    html_string = "<div class=\"box\"> \
    <article class=\"media\">\
      <figure class=\"media-left\">\
        <p class=\"image is-64x64\">\
          <img src=\"https://bulma.io/images/placeholders/128x128.png\">\
        </p>\
      </figure>\
      <div class=\"media-content\">\
        <div class=\"content\">\
          <p>\
            <strong>{}</strong> <small>@placeholder</small> <small>31m</small>\
            <br>\
            {}\
          </p>\
        </div>\
        <nav class=\"level is-mobile\">\
          <div class=\"level-left\">\
            <button class=\"button is-ghost\">edit</button>\
          </div>\
        </nav>\
      </div>\
      <div class=\"media-right\">\
        <button class=\"delete\"></button>\
      </div>\
    </article>\
 </div>".format(username, contents)  
 
    return html_string

# TODO function to get all comments a user made
def get_comments_user(user_id):
    return NULL

# TODO function to get all of a user's interactions with other posts
#      this will use get_comments_user()
# Return Null if error
def get_interactions_user(user_id):
    # Get things like comments, saving a post, reactions
    # and append them to each other

    # Then convert to html (special way for this specific grabber)
    # ^^^^ is to be done though
    return NULL

# TODO function to get all posts' id's of all topics a user is following
# Return Null if no topics followed
def get_posts_topics_followed(user_id):
    # For now just returns a list of 0->9
    user = User.query.filter_by(id=user_id)
    topics = user.followed_topics
    post_ids = list()

    for topic_id in topics:
          topic = Topic.query.filter_by(id=topic_id)
          for post in topic.post:
            post_ids.append(post)

    return post_ids

# TODO function to get all posts of a user
# Return Null if no/wrong id
def get_posts_user(user_id):
    # For now just returns a list of 0->9
    posts_for_user = Post.query.filter_by(user_id=user_id)
    result = []
    for post in posts_for_user:
      result.append(post.id)
    return result

# TODO function to get all posts' id's of all users a user is following
#      will end up using get_posts_user()
# Return Null if no users followed
def get_posts_users_followed(user_id):
    # For now just returns a list of 0->9
    cur_user = User.query.get(user_id)
    users = cur_user.followed.all()
    result = []
    for user in users:
      result += get_posts_user(user.id)
    return result

# Display the timeline of a user
@posts.route('/disp_userline/<id>/<post_num>/<type>')
def disp_userline(id, post_num, type):
    # Uses post_to_html, which converts a given post to its corresponding 
    # html to be placed in timeline.html by using post_list, which is a 
    # list of post id's, indexed by post_num
    post_list = NULL
    if (type == "Posts"):
        post_list = get_posts_user(id)
    elif (type == "Interactions"):
        post_list = get_interactions_user(id)
    if (post_list == NULL or len(post_list) == 0):
        flash('User has no content of that type')
        return redirect(url_for('prof.view_profile', id=id))

    # TODO add another elif for getting interactions
    post_num = int(post_num)
    list_len = len(post_list)
    post_html = post_to_html(post_list[post_num])

    return render_template('userline.html', id=id, post_num=post_num, post_html=post_html, type=type, list_len=list_len)


# Display the timeline of a user
@posts.route('/disp_timeline/<id>/<post_num>/<type>')
def disp_timeline(id, post_num, type):
    # Uses post_to_html, which converts a given post to its corresponding 
    # html to be placed in timeline.html by using post_list, which is a 
    # list of post id's, indexed by post_num
    post_list = NULL
    if (type == "Topic"):
        post_list = get_posts_topics_followed(id)
    elif (type == "Users"):
        post_list = get_posts_users_followed(id)
    if (post_list == NULL or len(post_list) == 0):
        flash('User has no content of that type')
        return redirect(url_for('prof.profile'))

    # TODO add another elif for getting interactions
    post_num = int(post_num)
    list_len = len(post_list)
    post_html = post_to_html(post_list[post_num])

    return render_template('timeline.html', id=id, post_num=post_num, post_html=post_html, type=type, list_len=list_len)


def get_urls(contents):
    url_list = re.findall(r'(https?://[^\s]+)', contents)
    return url_list