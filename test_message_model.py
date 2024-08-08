"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py

import os
from unittest import TestCase
from models import db, Message, User

os.environ['DATABASE_URL'] = "postgresql://shayan:shayan123@localhost:5432/warbler_test"

from app import app

with app.app_context():
    db.create_all()

class MessageModelTestCase(TestCase):
    """Test models for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            User.query.delete()
            Message.query.delete()
            db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""
        with app.app_context():
            u = User.signup(
                username="testuser",
                email="test@test.com",
                password="HASHED_PASSWORD",
                image_url=None
            )
            db.session.commit()

            m = Message(
                text="This is a test message",
                user_id=u.id
            )

            db.session.add(m)
            db.session.commit()

            self.assertEqual(len(u.messages), 1)
            self.assertEqual(u.messages[0].text, "This is a test message")
