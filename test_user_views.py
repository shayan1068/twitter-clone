"""User View tests."""

# run these tests like:
#
#    python -m unittest test_user_views.py

import os
from unittest import TestCase
from models import db, User

os.environ['DATABASE_URL'] = "postgresql://shayan:shayan123@localhost:5432/warbler_test"
os.environ['FLASK_ENV'] = "production"

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            db.create_all()
            User.query.delete()
            db.session.commit()

        self.client = app.test_client()

        with app.app_context():
            self.testuser = User.signup(username="testuser",
                                        email="test@test.com",
                                        password="testuser",
                                        image_url=None)
            db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            db.session.rollback()
            db.drop_all()

    def test_signup(self):
        """Can a user sign up?"""
        with self.client as c:
            resp = c.post("/signup", data={
                "username": "newuser",
                "email": "new@test.com",
                "password": "password",
                "image_url": None
            })

            self.assertEqual(resp.status_code, 302)

            with app.app_context():
                user = User.query.filter_by(username="newuser").first()
                self.assertIsNotNone(user)
                self.assertEqual(user.email, "new@test.com")
