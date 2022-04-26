import re
from time import sleep
from wsgiref.util import request_uri
from certifi import contents
from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask import session as cur_session
from flask_login import login_required, current_user
from requests import session
from .models import User, Post, Topic, Comment, post_topic, liked_post, saved_post
from . import db
from werkzeug.security import generate_password_hash

posts = Blueprint('posts', __name__)

NULL = 0
like_counter = 0
# redirect to post create page
# redirect to post create page
@posts.route('/create_post', methods=['POST'])
@login_required
def create_post():
    if request.form.get('action') == "Create Post":
      return render_template('create_post.html')

# post form connection
@posts.route('/post_created', methods=['POST'])
@login_required
def post_creation_handler():
    if request.form.get('action') == "Post Created": 
        topic = request.form.get('topic')
        contents = request.form.get('contents')
        anonymous = True if request.form.get('anonymous') == 'on' else False 

        if (anonymous):
          new_post = Post(user_id= -1, contents=contents, anonymous=anonymous, likes=0) 
        else:
          new_post = Post(user_id=current_user.id, contents=contents, anonymous=anonymous, likes=0)
        
        if (topic):
          topic_obj = Topic.query.filter_by(name=topic).first()
          # see if topic exists in db, if not create it
          if (not topic_obj):    
            topic_found = Topic(name=topic)
            db.session.add(topic_found) 
            new_post.tagged_topics.append(topic_found)
          else:
            new_post.tagged_topics.append(topic_obj)    
          
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('prof.profile'))

@posts.route('/delete_post/<id>', methods=['POST'])
@login_required
def delete_post(id):
  obj = Post.query.filter_by(id=id).first()
  print(f"VALUE: { obj.id }")
  # update relational databases
  q1 = post_topic.delete().where(post_topic.c.post_id == obj.id)
  db.session.execute(q1)
  db.session.commit()
  q2 = liked_post.delete().where(liked_post.c.liked_id == obj.id)
  db.session.execute(q2)
  db.session.commit()
  q3 = saved_post.delete().where(saved_post.c.saved_id == obj.id)
  db.session.execute(q3)
  db.session.commit()
  db.session.commit()
  # update Posts db
  db.session.delete(obj)
  db.session.commit()
  return redirect(url_for('prof.profile')) 


#Temporary gateway to view posts temporary display NOT FINAL
@posts.route('/view_temp', methods=['POST'])
@login_required
def view_temp():
    return render_template('posttemp.html')
  
# Function to get html to display a post AND a button to delete it
def post_del_to_html(post_id):
    #Currently done as <h3> because that is what lines up with in where the 
    #Post html is placed in timeline.html
    cur_session['url'] = request.url
    obj = Post.query.filter_by(id=post_id).first()
    user_for_post = User.query.filter_by(id=obj.user_id).first()
    tagged_topics = obj.tagged_topics
    tagged_topics_str = "Tags: "
    count = 0
    for topic in tagged_topics:
      count += 1    
      tagged_topics_str += topic.name
      if count < (len(tagged_topics)):
        tagged_topics_str += ", "
    contents = obj.contents
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
                <strong>" + str(username) + "</strong> <small>@placeholder</small> <small>31m</small>\
                <br>" + tagged_topics_str + "</p>\
                <br>" + str(contents) + "</p>\
            </div>\
            <nav class=\"level is-mobile\">\
              <div class=\"level-right\">\
                <form method=\"POST\" action=\"/delete_post/"+str(post_id)+"\">\
                  <button>Delete Post</button>\
                </form>\
              </div>\
            </nav>"
    comment_bar = "<form class=\"input-group\" method='POST' action=\"/create-comment/"+str(obj.id)+"\" >\
          <input type=\"text\" id=\"text\" name=\"text\" class =\"form-control\ placeholder=\"Comment something\" />\
          <button type=\"submit\" class=\"btn btn-primary\">Comment</button>  \
            <br>"
    html_string += comment_bar
    for comment in obj.comments:
      comments = comment.contents
      if current_user.id == comment.author:
        poster = current_user.name
      else:
        author = User.query.filter_by(id=comment.author).first()
        poster = author.name
      third_section = "<p><strong>" + str(poster) + ": </strong>" + str(comments) + ""
      if current_user.id == comment.author or current_user == obj.user_id:
        fourth_section = "&nbsp; &nbsp; <a href=\"/delete-comment/"+str(comment.id)+"\" style=\"color:red\">Delete</a></p>"
      else:
        fourth_section = ''
      html_string += third_section
      html_string += fourth_section
    
    
    end = "</div>\
          <div class=\"media-right\">\
            <button class=\"delete\"></button>\
          </div>\
        </article>\
        </div>"
    html_string += end

    return html_string

#Function to get html to display a post
def post_to_html(post_id):
    #Currently done as <h3> because that is what lines up with in where the 
    #Post html is placed in timeline.html
    cur_session['url'] = request.url
    obj = Post.query.filter_by(id=post_id).first()
    user_for_post = User.query.filter_by(id=obj.user_id).first()
    tagged_topics = obj.tagged_topics
    tagged_topics_str = "Tags: "
    count = 0
    for topic in tagged_topics:
      count += 1    
      tagged_topics_str += topic.name
      if count < (len(tagged_topics)):
        tagged_topics_str += ", "
    contents = obj.contents
    likes = obj.likes
    # topics = obj.topic_list.split(',') // no longer needed, switched to post_topic rdb
    username = user_for_post.name

    html_string_unliked_saved = ""
    html_string_unliked_unsaved = ""
    html_string_liked_saved = ""
    html_string_liked_unsaved = ""

    html_string_unliked_unsaved = "<div class=\"box\"> \
        <article class=\"media\">\
          <figure class=\"media-left\">\
            <p class=\"image is-64x64\">\
              <img src=\"https://bulma.io/images/placeholders/128x128.png\">\
            </p>\
          </figure>\
          <div class=\"media-content\">\
            <div class=\"content\">\
              <p>\
                <strong>" + str(username) + "</strong> <small>@placeholder</small> <small>31m</small>\
                <br>" + tagged_topics_str + "</p>\
                <br>" + str(contents) + "</p>\
            </div>\
            <nav class=\"level is-mobile\">\
              <div class=\"level-right\">\
                <form action=\"/see_full_post/"+str(post_id)+"\">\
                  <button>post details</button>\
                </form>\
              </div>\
              <div class=\"level-right\">\
                <form action=\"/save_post/"+str(post_id)+"\">\
                  <button>Save</button>\
                </form>\
              </div>\
              <div class=\"level-right\">\
                <form action=\"/like_post/"+str(post_id)+"\">\
                  <button>Like</button>\
                </form>\
              <div class=\"content\">\
              <p>\
                Likes: " + str(likes) + "</p>\
            </div>\
            </nav>"

    comment_bar = "<form class=\"input-group\" method='POST' action=\"/create-comment/"+str(obj.id)+"\" >\
          <input type=\"text\" id=\"text\" name=\"text\" class =\"form-control\ placeholder=\"Comment something\" />\
          <button type=\"submit\" class=\"btn btn-primary\">Comment</button>  \
            <br>"
    html_string_unliked_unsaved += comment_bar
    for comment in obj.comments:
      comments = comment.contents
      if current_user.id == comment.author:
        poster = current_user.name
      else:
        author = User.query.filter_by(id=comment.author).first()
        poster = author.name
      third_section = "<p><strong>" + str(poster) + ": </strong>" + str(comments) + ""
      if current_user.id == comment.author or current_user == obj.user_id:
        fourth_section = "&nbsp; &nbsp; <a href=\"/delete-comment/"+str(comment.id)+"\" style=\"color:red\">Delete</a></p>"
      else:
        fourth_section = ''
      html_string_unliked_unsaved += third_section
      html_string_unliked_unsaved += fourth_section
    
    
    end = "</div>\
          <div class=\"media-right\">\
            <button class=\"delete\"></button>\
          </div>\
        </article>\
        </div>"
    html_string_unliked_unsaved += end
    
    html_string_unliked_saved = "<div class=\"box\"> \
        <article class=\"media\">\
          <figure class=\"media-left\">\
            <p class=\"image is-64x64\">\
              <img src=\"https://bulma.io/images/placeholders/128x128.png\">\
            </p>\
          </figure>\
          <div class=\"media-content\">\
            <div class=\"content\">\
              <p>\
                <strong>" + str(username) + "</strong> <small>@placeholder</small> <small>31m</small>\
                <br>" + tagged_topics_str + "</p>\
                <br>" + str(contents) + "</p>\
            </div>\
            <nav class=\"level is-mobile\">\
              <div class=\"level-right\">\
                <form action=\"/see_full_post/"+str(post_id)+"\">\
                  <button>post details</button>\
                </form>\
              </div>\
              <div class=\"level-right\">\
                <form action=\"/unsave_post/"+str(post_id)+"\">\
                  <button>Unsave</button>\
                </form>\
              </div>\
              <div class=\"level-right\">\
                <form action=\"/like_post/"+str(post_id)+"\">\
                  <button>Like</button>\
                </form>\
              <div class=\"content\">\
              <p>\
                Likes: " + str(likes) + "</p>\
            </div>\
            </nav>"

    html_string_unliked_saved += comment_bar
    for comment in obj.comments:
      comments = comment.contents
      if current_user.id == comment.author:
        poster = current_user.name
      else:
        author = User.query.filter_by(id=comment.author).first()
        poster = author.name
      third_section = "<p><strong>" + str(poster) + ": </strong>" + str(comments) + ""
      if current_user.id == comment.author or current_user == obj.user_id:
        fourth_section = "&nbsp; &nbsp; <a href=\"/delete-comment/"+str(comment.id)+"\" style=\"color:red\">Delete</a></p>"
      else:
        fourth_section = ''
      html_string_unliked_saved += third_section
      html_string_unliked_saved += fourth_section
    
    
    html_string_unliked_saved += end

    html_string_liked_saved = "<div class=\"box\"> \
      <article class=\"media\">\
        <figure class=\"media-left\">\
          <p class=\"image is-64x64\">\
            <img src=\"https://bulma.io/images/placeholders/128x128.png\">\
          </p>\
        </figure>\
        <div class=\"media-content\">\
          <div class=\"content\">\
            <p>\
              <strong>" + str(username) + "</strong> <small>@placeholder</small> <small>31m</small>\
              <br>" + tagged_topics_str + "</p>\
              <br>" + str(contents) + "</p>\
          </div>\
          <nav class=\"level is-mobile\">\
            <div class=\"level-right\">\
              <form action=\"/see_full_post/"+str(post_id)+"\">\
                <button>post details</button>\
              </form>\
            </div>\
            <div class=\"level-right\">\
              <form action=\"/unsave_post/"+str(post_id)+"\">\
                <button>Unsave</button>\
              </form>\
            </div>\
            <div class=\"level-right\">\
              <form action=\"/unlike_post/"+str(post_id)+"\">\
                <button>Dislike</button>\
              </form>\
            <div class=\"content\">\
            <p>\
              Likes: " + str(likes) + "</p>\
          </div>\
          </nav>"
    html_string_liked_saved += comment_bar
    for comment in obj.comments:
      comments = comment.contents
      if current_user.id == comment.author:
        poster = current_user.name
      else:
        author = User.query.filter_by(id=comment.author).first()
        poster = author.name
      third_section = "<p><strong>" + str(poster) + ": </strong>" + str(comments) + ""
      if current_user.id == comment.author or current_user == obj.user_id:
        fourth_section = "&nbsp; &nbsp; <a href=\"/delete-comment/"+str(comment.id)+"\" style=\"color:red\">Delete</a></p>"
      else:
        fourth_section = ''
      html_string_liked_saved += third_section
      html_string_liked_saved += fourth_section
    
    
    html_string_liked_saved += end

    html_string_liked_unsaved = "<div class=\"box\"> \
      <article class=\"media\">\
        <figure class=\"media-left\">\
          <p class=\"image is-64x64\">\
            <img src=\"https://bulma.io/images/placeholders/128x128.png\">\
          </p>\
        </figure>\
        <div class=\"media-content\">\
          <div class=\"content\">\
            <p>\
              <strong>" + str(username) + "</strong> <small>@placeholder</small> <small>31m</small>\
              <br>" + tagged_topics_str + "</p>\
              <br>" + str(contents) + "</p>\
          </div>\
          <nav class=\"level is-mobile\">\
            <div class=\"level-right\">\
              <form action=\"/see_full_post/"+str(post_id)+"\">\
                <button>post details</button>\
              </form>\
            </div>\
            <div class=\"level-right\">\
              <form action=\"/save_post/"+str(post_id)+"\">\
                <button>Save</button>\
              </form>\
            </div>\
            <div class=\"level-right\">\
              <form action=\"/unlike_post/"+str(post_id)+"\">\
                <button>Dislike</button>\
              </form>\
            <div class=\"content\">\
            <p>\
              Likes: " + str(likes) + "</p>\
          </div>\
          </nav>"
    html_string_liked_unsaved += comment_bar
    for comment in obj.comments:
      comments = comment.contents
      if current_user.id == comment.author:
        poster = current_user.name
      else:
        author = User.query.filter_by(id=comment.author).first()
        poster = author.name
      third_section = "<p><strong>" + str(poster) + ": </strong>" + str(comments) + ""
      if current_user.id == comment.author or current_user == obj.user_id:
        fourth_section = "&nbsp; &nbsp; <a href=\"/delete-comment/"+str(comment.id)+"\" style=\"color:red\">Delete</a></p>"
      else:
        fourth_section = ''
      html_string_liked_unsaved += third_section
      html_string_liked_unsaved += fourth_section
    
    
    html_string_liked_unsaved += end

    if current_user.is_liking(obj): # user does not like post
      if current_user.has_saved(obj):
        html_string = html_string_liked_saved
      else:
        html_string = html_string_liked_unsaved
    else:
      if current_user.has_saved(obj):
        html_string = html_string_unliked_saved
      else:
        html_string = html_string_unliked_unsaved
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

    # Get post id's of liked posts
    liked_posts_ids = []
    user = User.query.filter_by(id=user_id).first()
    for liked_post in user.liked:
      liked_posts_ids.append(liked_post.id)

    # Then convert to html (special way for this specific grabber)
    # ^^^^ is to be done though
    return NULL

# TODO function to get all posts' id's of all topics a user is following
# Return Null if no topics followed
def get_posts_topics_followed(user_id):  
    user = User.query.filter_by(id=user_id).first()
    # topics is a list of Topic objects
    topics = user.followed_topics.all()
    # list containing post ids
    post_ids = []
    blocked_user_ids = []
    blocked_users = user.blocked.all()
    for blocked_user in blocked_users:
      blocked_user_ids.append(blocked_user.id)
    for topic in topics:
      post_list = topic.posts
      for post in post_list:
        if (post.user_id in blocked_user_ids):
          continue
        post_ids.append(post.id)
      # endfor
    # endfor
    return post_ids

# TODO function to get all posts of a user
# Return Null if no/wrong id
def get_posts_user(user_id):
    posts_for_user = Post.query.filter_by(user_id=user_id)
    result = []
    for post in posts_for_user:
      result.append(post.id)
    return result

# TODO function to get all posts' id's of all users a user is following
#      will end up using get_posts_user()
# Return Null if no users followed
def get_posts_users_followed(user_id):
    cur_user = User.query.get(user_id)
    users = cur_user.followed.all()
    if len(users) == 0:
      flash('No followed?')    
    result = list()
    for user in users:
      if user.is_blocking(user):
        continue
      for post in get_posts_user(user.id):   
        result.append(post)
    return result
  
# Manage posts function
@posts.route('/manage_posts/<id>/<post_num>')
def manage_posts(id, post_num):
    posts = Post.query.filter_by(user_id=id).all()
    post_list = []
    for post in posts:
        post_list.append(post.id)
    if len(post_list) == 0:
        flash("You haven't created any posts yet!")
        return redirect(url_for('prof.profile'))
    post_num = int(post_num)
    list_len = len(post_list)
    post_html = post_del_to_html(post_list[post_num])
    return render_template('manage_posts.html', id = id, post_num=post_num, post_html=post_html, list_len=list_len)
# added above for manage posts

# Display timeline of saved posts
@posts.route('/saved_posts/<id>/<post_num>')
def view_saved_posts(id, post_num):
    obj = User.query.get(id)    
    post_list = []
    for post in obj.saved_posts:
        post_list.append(post.id)
    if len(post_list) == 0:
        flash('No Saved Posts exist!')
        return redirect(url_for('prof.profile'))
    post_num = int(post_num)
    list_len = len(post_list)
    post_html = post_to_html(post_list[post_num])
    return render_template('saved_posts.html', id = id, post_num=post_num, post_html=post_html, list_len=list_len)


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

@posts.route('/like_post/<id>')
def like_post(id):
    post = Post.query.filter_by(id=id).first()
    if current_user.is_liking(post):
        flash('Hey buddy I know you like this guy, but you\'re already liking them')
        return redirect(url_for('prof.view_profile', id=id))
    post.likes += 1
    current_user.like(post)
    db.session.commit()
    if 'url' in cur_session:
      return redirect(cur_session['url'])
    else:
      return redirect(url_for('prof.view_profile', id=id))

@posts.route('/unlike_post/<id>')
def unlike_post(id):
    post = Post.query.filter_by(id=id).first()
    if post is None:
        return redirect(url_for('index', id=id))
    post.likes -= 1
    current_user.unlike(post)
    db.session.commit()
    if 'url' in cur_session:
      return redirect(cur_session['url'])
    else:
      return redirect(url_for('prof.view_profile', id=id))

@posts.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
  contents = request.form.get('text')

  if not contents:
    flash('Comment cannot be empty!', category='error')
  else:
    post = Post.query.filter_by(id=post_id)
    if post:
      comment = Comment(contents=contents, author=current_user.id, post_id=post_id)
      db.session.add(comment)
      db.session.commit()
    
  return redirect(cur_session['url'])

@posts.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
  comment = Comment.query.filter_by(id=comment_id).first()

  if not comment:
    flash('Comment does not exist')
  else:
    db.session.delete(comment)
    db.session.commit()

  return redirect(cur_session['url'])
# Added below for save post functionality

@posts.route('/save_post/<id>')
def save_post(id):
    post = Post.query.filter_by(id=id).first()
    if current_user.has_saved(post):
        flash('Hey buddy I know you like this post, but you\'ve already saved this!')
        return redirect(url_for('prof.view_profile', id=id))
    current_user.save(post)
    db.session.commit()
    if 'url' in cur_session:
      return redirect(cur_session['url'])
    else:
      return redirect(url_for('prof.view_profile', id=id))

@posts.route('/unsave_post/<id>')
def unsave_post(id):
    post = Post.query.filter_by(id=id).first()
    if post is None:
        return redirect(url_for('index', id=id))
    current_user.unsave(post)
    db.session.commit()
    if 'url' in cur_session:
      return redirect(cur_session['url'])
    else:
      return redirect(url_for('prof.view_profile', id=id))

# Added above for save post functionality

def get_urls(contents):
    url_list = re.findall(r'(https?://[^\s]+)', contents)
    return url_list