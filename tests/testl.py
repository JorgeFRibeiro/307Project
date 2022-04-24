from datetime import datetime, timedelta
import unittest
from __init__ import app, db
from models import User, Post

class UserModelCase(unittest.TestCase):
    print("Running tests...")
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_follow(self):
        u1 = User(email='james@example.com', name='james', password='james1')
        u2 = User(email='pierre@example.com', name='pierre', password='pierre1')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'pierre')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'james')

    def test_unfollow(self):
        u1 = User(email='daniel@example.com', name='daniel', password='daniel1')
        u2 = User(email='ryan@example.com', name='ryan', password='ryan1')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().name, 'pierre')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().name, 'james')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        p1 = Post(contents="post from john", user_id=u1.id,
                  topic_list="funtime,testing")
        p2 = Post(contents="post from susan", user_id=u2.id,
                  topic_list="funtime,testing")
        p3 = Post(contents="post from mary", user_id=u3.id,
                  topic_list="funtime,testing")
        p4 = Post(contents="post from david", user_id=u4.id,
                  topic_list="funtime,testing")
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

class UserModelCaseII(unittest.TestCase):
    print("Running tests...")
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_follow_topic(self):
        u1 = User(email='james@example.com', name='james', password='james1')
        u2 = User(email='pierre@example.com', name='pierre', password='pierre1')
        db.session.add(u1)
        db.session.add(u2)
        p1 = Post(contents="post from pierre", user_id=u2.id,
                  topic_list="funtime,testing")
        db.session.add(p1)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow_topic(p1.topic_list)
        db.session.commit()
        self.assertTrue(u1.is_following_topic(p1.topic_list))
        self.assertEqual(u1.topic_followed.count(), 1)
        self.assertEqual(u1.followed.first().topic, 'funtime')

    def test_unfollow_topic(self):
        u1 = User(email='james@example.com', name='james', password='james1')
        u2 = User(email='pierre@example.com', name='pierre', password='pierre1')
        db.session.add(u1)
        db.session.add(u2)
        p1 = Post(contents="post from pierre", user_id=u2.id,
                  topic_list="funtime,testing")
        db.session.add(p1)
        db.session.commit()
        self.assertEqual(u1.followed_topics.all(), [])
        self.assertEqual(u1.topic_followers.all(), [])

        u1.follow_topic(p1.topic_list)
        db.session.commit()
        self.assertTrue(u1.is_following(p1.topic_list))
        self.assertEqual(u1.topic_followed.count(), 1)
        self.assertEqual(u1.followed.first().topic, 'funtime')

        u1.unfollow_topic(p1.topic_list)
        db.session.commit()
        self.assertFalse(u1.is_following_topic())
        self.assertEqual(u1.followed_topics.count(), 0)

    def is_following_topic(self):
        # create four users
        u1 = User(email='cole@example.com', name='cole', password='cole1')
        u2 = User(email='julia@example.com', name='julia', password='julia1')
        db.session.add(u1)
        db.session.add(u2)
        p1 = Post(contents="post from pierre", user_id=u2.id,
                  topic_list="funtime,testing")
        db.session.add(p1)
        db.session.commit()

        u1.follow_topic(p1.topic_list)
        db.session.commit()
        self.assertTrue(u1.is_following_topic(p1.topic_list))


if __name__ == '__main__':
    unittest.main(verbosity=2)