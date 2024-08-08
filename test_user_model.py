"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os
from unittest import TestCase
import logging

from models import db, User, Message, Follows

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql://shayan:shayan123@localhost:5432/warbler_test"

# Now we can import app
from app import app

class UserModelTestCase(TestCase):
    """Test views for messages."""

    @classmethod
    def setUpClass(cls):
        """Set up database for tests."""
        with app.app_context():
            logging.info("Creating all tables for the test database.")
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Tear down database after tests."""
        with app.app_context():
            logging.info("Dropping all tables for the test database.")
            db.drop_all()

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            logging.info("Deleting existing data and setting up new data for tests.")
            User.query.delete()
            Message.query.delete()
            Follows.query.delete()
            db.session.commit()

            self.client = app.test_client()

            self.u1 = User.signup("testuser1", "test1@test.com", "password", None)
            self.u2 = User.signup("testuser2", "test2@test.com", "password", None)
            db.session.commit()

            self.u1 = User.query.get(self.u1.id)
            self.u2 = User.query.get(self.u2.id)

    def tearDown(self):
        """Clean up fouled transactions."""
        with app.app_context():
            logging.info("Rolling back any fouled transactions.")
            db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""
        with app.app_context():
            logging.info("Testing basic user model.")
            u = User(email="test3@test.com", username="testuser3", password="HASHED_PASSWORD")
            db.session.add(u)
            db.session.commit()

            self.assertEqual(len(u.messages), 0)
            self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """Does the repr method work as expected?"""
        with app.app_context():
            logging.info("Testing repr method.")
            u1 = User.query.get(self.u1.id)
            self.assertEqual(repr(u1), f"<User #{u1.id}: testuser1, test1@test.com>")

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""
        with app.app_context():
            logging.info("Testing is_following method.")
            u1 = User.query.get(self.u1.id)
            u2 = User.query.get(self.u2.id)
            u1.following.append(u2)
            db.session.commit()

            self.assertTrue(u1.is_following(u2))
            self.assertFalse(u2.is_following(u1))

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""
        with app.app_context():
            logging.info("Testing is_followed_by method.")
            u1 = User.query.get(self.u1.id)
            u2 = User.query.get(self.u2.id)
            u2.following.append(u1)
            db.session.commit()

            self.assertTrue(u1.is_followed_by(u2))
            self.assertFalse(u2.is_followed_by(u1))

    def test_signup(self):
        """Does User.signup successfully create a new user given valid credentials?"""
        with app.app_context():
            logging.info("Testing User.signup method.")
            u = User.signup("testuser3", "test3@test.com", "password", None)
            db.session.commit()

            self.assertIsNotNone(User.query.get(u.id))

    def test_authenticate(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        with app.app_context():
            logging.info("Testing User.authenticate method.")
            self.assertTrue(User.authenticate("testuser1", "password"))
            self.assertFalse(User.authenticate("testuser1", "wrongpassword"))
            self.assertFalse(User.authenticate("wrongusername", "password"))
