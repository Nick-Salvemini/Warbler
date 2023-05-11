"""User model tests."""

# run these tests like:
#
#    python3 -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase

from models import db, User, Message, Follows

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        """Does the repr for the user model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        user_repr = repr(u)

        self.assertEqual(user_repr, f"<User #{u.id}: testuser, test@test.com>")

    def test_is_following_and_followed_by(self):
        """Does is_following and is_followed_by properly track if a user is following another user"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.add(u2)
        db.session.commit()

        self.assertFalse(User.query.get(u.id).is_following(u2.id))
        self.assertFalse(User.query.get(u2.id).is_followed_by(u.id))

        f = Follows(user_being_followed_id=u2.id, user_following_id=u.id)

        db.session.add(f)
        db.session.commit()

        user_following = u.is_following(u2)
        user_is_followed = u2.is_followed_by(u)

        self.assertTrue(user_following)
        self.assertTrue(user_is_followed)

    def test_signup(self):
        """Does signup work only when valid info is given"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="test2user",
            password="HASHED_PASSWORD"
        )

        User.signup(u.email, u.username, u.password, u.image_url)
        print(u)
        db.session.commit()

        User.signup(u2.email, u2.username, u2.password)
        print(u2)
        db.session.commit()

        self.assertTrue(u2)
