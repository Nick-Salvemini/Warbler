"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest test_user_views.py


from app import app, CURR_USER_KEY
import os
from unittest import TestCase
from flask import Flask, current_app

from models import db, connect_db, Message, User, Follows


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        # app.testing = True
        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                     email="test2@test.com",
                                     password="test2user",
                                     image_url=None)

        db.session.commit()

        self.follow = Follows(user_being_followed_id=self.testuser2.id,
                              user_following_id=self.testuser.id)

        self.follow2 = Follows(user_being_followed_id=self.testuser.id,
                               user_following_id=self.testuser2.id)

        db.session.add(self.follow, self.follow2)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        # app.testing = False

    def test_list_users(self):
        """"Does list users work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get('/users')

        self.assertEqual(resp.status_code, 200)
        self.assertIn("@testuser", str(resp.data))

    def test_show_users(self):
        """Does the route show the individual user"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get(f'/users/{self.testuser.id}')

        self.assertEqual(resp.status_code, 200)
        self.assertIn("@testuser", str(resp.data))

    def test_show_following(self):
        """Does the route show who the user is following"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get(f'/users/{self.testuser.id}/following')

        print('******', self.testuser)
        # print('xxxxxxx', self.testuser2)

        # follow = self.testuser.is_following(self.testuser2)

        # db.session.add(follow)
        # db.session.commit()

        # testuser2 = User.signup(username="testuser2",
        #                         email="test2@test.com",
        #                         password="test2user",
        #                         image_url=None)

        # db.session.commit()

        # follow = Follows(user_being_followed_id=testuser2,
        #                  user_following_id=self.testuser)

        # db.session.add(follow)
        # db.session.commit()

        # follow = self.testuser.is_following(testuser2)

        print('*******', self.testuser.following)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("@testuser", str(resp.data))
        # self.assertIn("@test2user", str(resp.data))

    def test_users_followers(self):
        """Does the route show the followers of the user"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get(f'/users/{self.testuser.id}/followers')

        self.assertEqual(resp.status_code, 200)

    def test_users_liked_messages(self):
        """Does the route show users liked messages"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get(f'/users/{self.testuser.id}/likes')

        self.assertEqual(resp.status_code, 200)

    # def test_add_follow(self):
    #     """Does the route add a new follow to the current user"""

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id

    #        resp = c.get(f'/users/follow/{self.testuser.id}')

    #        self.assertEqual(resp.status_code, 200)

    # def test_stop_following(self):

    # def test_profile(self):

    # def test_delete_user(self):
