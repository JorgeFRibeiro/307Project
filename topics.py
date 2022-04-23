from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import login_required, current_user
from .models import User, Post, Topic
from . import db

topics = Blueprint('topics', __name__)

# Gets a list of all topic names
def existing_topics_names():
    topic_list = []
    for topic_name in Topic.query.distinct(Topic.name):
        topic_list.append(topic_name.name)
    return topic_list

# Gets a list of all topic ids
def existing_topics_ids():
    topic_list = []
    for topic in Topic.query:
        topic_list.append(topic.id)
    return topic_list

# Convert topic to html for box in all-topics page
def topic_to_html(name, id):
    # html conversion
    html_string =  "<div class=\"box\">\
                        <h3>" + str(name) + "</h3>\
                        <form action=\"/view_topic/" + str(id) + "\">\
                            <button>View this Topic</button>\
                        </form>\
                    </div>"
    return html_string

# Display all currently available topics
@topics.route('/all_topics_page')
def all_topics_page():
    topics_ids = existing_topics_ids()
    topics_names = existing_topics_names()
    topics_html_string = ""
    if len(topics_ids) == 0:
        topics_html_string += "<div class=\"box\">\
                                    <h3>No topics exist at the moment!</h3>\
                                </div>"
    else:
        for i in range(0, len(topics_ids)):
            cur_topic_name = topics_names[i]
            cur_topic_id = topics_ids[i]
            topics_html_string += topic_to_html(cur_topic_name, cur_topic_id)
    return render_template('topics_page.html', topics_string=topics_html_string)

# Display all posts under a topic
@topics.route('/view_topic/<id>')
def view_topic(id):
    topic_to_view = Topic.query.get(id)
    return render_template('topic.html', name = topic_to_view.name, id = id)
