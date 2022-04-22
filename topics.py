from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import login_required, current_user
from .models import User, Post, Topic
from . import db

topics = Blueprint('topics', __name__)

# Gets a list of all topic names
def existing_topics_names():
    topic_list = []
    for topic_name in Topic.query(Topic.name).distinct():
        topic_list.append(topic_name)
    return topic_list

# Gets a list of all topic ids
def existing_topics_ids():
    topic_list = []
    for topic in Topic.query:
        topic_list.append(topic.id)
    return topic_list

# Convert topic to html for box in all-topics page
def topic_to_html(topic):
    # html conversion
    html_string =  "<div class=\"box\">\
                        <h3>" + str(topic) + "</h3>\
                        <form action=\"/view_topic/" + str(topic) + "\">\
                            <button>View this Topic</button>\
                        </form>\
                    </div>"
    return html_string

# Display all currently available topics
@topics.route('/all_topics_page')
def all_topics_page():
    topics = existing_topics_ids()
    topics_html_string = ""
    if len(topics) == 0:
        topics_html_string += "<div class=\"box\">\
                                    <h3>No topics exist at the moment!</h3>\
                                </div>"
    else:
        for cur_topic in topics:
            topics_html_string += topic_to_html(cur_topic)
    return render_template('topics_page.html', topics_string=topics_html_string)

# Display all posts under a topic
@topics.route('/view_topic/<topic>')
def view_topic():
    return render_template('index.html')
