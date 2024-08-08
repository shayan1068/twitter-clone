"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py

import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql://shayan:shayan123@localhost:5432/warbler_test"

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    @classmethod
    def setUpClass(cls):
        """Set up database for tests."""
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Tear down database after tests."""
        with app.app_context():
            db.drop_all()

    def setUp(self):
        """Create test client, add sample data."""
        self.client = app.test_client()

        with app.app_context():
            User.query.delete()
            Message.query.delete()
            db.session.commit()

            self.testuser = User.signup(username="testuser",
                                        email="test@test.com",
                                        password="testuser",
                                        image_url=None)
            db.session.commit()
            self.testuser = User.query.filter_by(username="testuser").first()

    def tearDown(self):
        """Clean up fouled transactions."""
        with app.app_context():
            db.session.rollback()

    def test_add_message(self):
        """Can use add a message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)

            with app.app_context():
                msg = Message.query.one()
                self.assertEqual(msg.text, "Hello")

    def test_logged_in_add_message(self):
        """When you're logged in, can you add a message as yourself?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            with app.app_context():
                msg = Message.query.filter_by(text="Hello").one()
                self.assertIsNotNone(msg)
                self.assertEqual(msg.user_id, self.testuser.id)

    def test_logged_out_add_message(self):
        """When you're logged out, are you prohibited from adding messages?"""
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_logged_in_delete_message(self):
        """When you're logged in, can you delete a message as yourself?"""
        with app.app_context():
            msg = Message(text="Hello", user_id=self.testuser.id)
            db.session.add(msg)
            db.session.commit()

            msg = Message.query.filter_by(text="Hello").first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            with app.app_context():
                self.assertIsNone(db.session.get(Message, msg.id))

    def test_logged_out_delete_message(self):
        """When you're logged out, are you prohibited from deleting messages?"""
        with app.app_context():
            msg = Message(text="Hello", user_id=self.testuser.id)
            db.session.add(msg)
            db.session.commit()

            msg = Message.query.filter_by(text="Hello").first()

        with self.client as c:
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            with app.app_context():
                self.assertIsNotNone(db.session.get(Message, msg.id))

    def test_delete_message_as_another_user(self):
        """When you're logged in, are you prohibited from deleting a message as another user?"""
        with app.app_context():
            u2 = User.signup(username="testuser2", email="test2@test.com", password="testuser", image_url=None)
            db.session.commit()
            u2 = User.query.filter_by(username="testuser2").first()

            msg = Message(text="Hello", user_id=u2.id)
            db.session.add(msg)
            db.session.commit()

            msg = Message.query.filter_by(text="Hello").first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            with app.app_context():
                self.assertIsNotNone(db.session.get(Message, msg.id))

    def test_view_follower_following_pages(self):
        """When you're logged in, can you see the follower/following pages for any user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}/followers")
            self.assertEqual(resp.status_code, 200)

            resp = c.get(f"/users/{self.testuser.id}/following")
            self.assertEqual(resp.status_code, 200)

    def test_logged_out_view_follower_following_pages(self):
        """When you're logged out, are you disallowed from visiting a user's follower/following pages?"""
        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            resp = c.get(f"/users/{self.testuser.id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
