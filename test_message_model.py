"""Message model tests."""

# run these tests like:
#
#    python3 -m unittest test_message_model.py


from app import app
import os
from unittest import TestCase

from models import db, User, Message, Likes

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


class MessageModelTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        u_model = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        self.u = User.signup(u_model.username, u_model.email,
                             u_model.password, u_model.image_url)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):

        u = self.u

        m = Message(text='Test message.', user_id=u.id)
        db.session.add(m)
        db.session.commit()

        self.assertTrue(m)
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, 'Test message.')

    def test_message_likes(self):

        u = self.u

        m = Message(text='Test message.', user_id=u.id)
        db.session.add(m)
        db.session.commit()

        l = Likes(user_id=u.id, message_id=m.id)
        db.session.add(l)
        db.session.commit()

        self.assertEqual(len(self.u.likes), 1)
        self.assertEqual(self.u.likes[0].id, l.id)
        self.assertEqual(l.message_id, m.id)
        self.assertEqual(l.user_id, u.id)
