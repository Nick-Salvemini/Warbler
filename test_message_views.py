"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest test_message_views.py


from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes

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


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

            resp2 = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp2.status_code, 500)

    def test_show_message(self):
        """Do messages show properly?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            m = Message(text='Test message', user_id=self.testuser.id)
            db.session.add(m)
            db.session.commit()

            resp = c.get(f"/messages/{m.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn(m.text, resp.get_data(as_text=True))

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

            resp2 = c.get(f"/messages/{m.id}")

            self.assertEqual(resp2.status_code, 500)

    def test_delete_message(self):
        """Are messages properly delete?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            m = Message(text='Test message', user_id=self.testuser.id)
            db.session.add(m)
            db.session.commit()

            resp = c.post(f'/messages/{m.id}/delete')

            self.assertEqual(resp.status_code, 302)

            msg = Message.query.get(m.id)

            self.assertFalse(msg)

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

            resp2 = c.post(f'/messages/{m.id}/delete')

            self.assertEqual(resp2.status_code, 500)

    def test_like_and_unlike_message(self):
        """Are messages liked and unliked?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            m = Message(text='Test message', user_id=self.testuser.id)
            db.session.add(m)
            db.session.commit()

            resp = c.post(f'/users/add_like/{m.id}')

            q = Likes.query.filter(Likes.message_id == m.id).first()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(self.testuser.id, q.user_id)

            resp2 = c.post(f'/users/add_like/{m.id}')

            q2 = Likes.query.filter(Likes.message_id == m.id).first()

            self.assertEqual(resp2.status_code, 302)
            self.assertFalse(q2)

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

            resp3 = c.post(f'/users/add_like/{m.id}')

            self.assertEqual(resp3.status_code, 500)
