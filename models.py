from flask_login import UserMixin
from . import db

# User model that stores information regarding the person logged in atm
# TODO: Connect to database, Make fields actually what we need, will require
#       edits to signup.html and auth.py for user field changes 

# Followers association table
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# Topics association table, foreign key -> link btw two tables
user_topic = db.Table('user_topic',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('topic_id', db.integer, db.ForeignKey('topic.id'))
)

# Topics association table, foreign key -> link btw two tables
post_topic = db.Table('post_topic',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('topic_id', db.integer, db.ForeignKey('topic.id'))
)

class User(UserMixin, db.Model):

    # Some of these fields are required
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    bio = db.Column(db.String(1000))
    # End of warning

    followed_topics = db.relationship('Topic', secondary=user_topic, backref='followed_by')

    # Included many to many follower relationship
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def posts_with_followed_topics(self):
        #TODO

    # Adding follower
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    # Removing follower
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    # Cannot follow twice if already followed
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    # Obtaining posts from followed users while having own post
    # in the timeline as well
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.id.desc())


class Post(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    contents = db.Column(db.String(300))
    topic_list = db.Column(db.String(1000)) #going to be stored in this format "topic1,topic2,topic3", use split() function
    tagged_topics = db.relationship('Topic', secondary=post_topic, backref='posts_tagged_with')

    def get_tagged_posts(self, topic):
        list = Post.query.filter

class Topic(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    posts = db.relationship('Posts', secondary=post_topic, backref='tags_mentioned')
    users = db.relationship('Users', secondary=user_topic, backref='tags_followed')