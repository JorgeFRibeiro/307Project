from email.policy import default
from flask_login import UserMixin
from . import db

# User model that stores information regarding the person logged in atm
# TODO: Connect to database, Make fields actually what we need, will require
#       edits to signup.html and auth.py for user field changes 

class User(UserMixin, db.Model):

    # Some of these fields are required
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    bio = db.Column(db.String(1000))
    confirmed = db.Column(db.Boolean, nullable = False, default = False)
    confirmed_on = db.Column(db.DateTime)
    # End of warning

class Post(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    contents = db.Column(db.String(300))
    topic_list = db.Column(db.String(1000)) #going to be stored in this format "topic1,topic2,topic3", use split() function