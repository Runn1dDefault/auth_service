import unittest
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dao.controllers import UserController
from dao.models import User

TEST_DB_URI = 'sqlite:///:memory:'


class TestUserController(unittest.TestCase):
    def setUp(self):
        engine_test = create_engine(TEST_DB_URI)
        User.metadata.create_all(engine_test)

        session_test = sessionmaker()
        session_test.configure(binds={User: engine_test})
        self.session_test = session_test()

        self.user_controller = UserController(session=self.session_test)

    def tearDown(self):
        self.user_controller.close()

    def test_create_user(self):
        user_data = {
            'email': 'controller_test_user@example.com',
            'password': 'test_password',
            'role': 'user',
            'full_name': "User Name",
            'email_verified': False,
            'is_active': True,
            'joined_at': datetime.utcnow()
        }
        user = User(**user_data)
        self.user_controller.create(user)
        created_user = self.session_test.query(User).filter_by(email='controller_test_user@example.com').first()
        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.email, 'controller_test_user@example.com')

    def test_get_all_users(self):
        users = self.user_controller.get_all()
        self.assertIsInstance(users, list)

    def test_get_user_by_id(self):
        user_data = {
            'email': 'controller_test_id_user@example.com',
            'password': 'test_password',
            'role': 'user',
            'full_name': "User Name",
            'email_verified': True,
            'is_active': True,
            'joined_at': datetime.utcnow()
        }
        user = User(**user_data)
        self.session_test.add(user)
        self.session_test.commit()
        retrieved_user = self.user_controller.get_by_id(user.id)

        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.id, user.id)

    def test_user_by_email(self):
        user_data = {
            'email': 'controller_test_email_user@example.com',
            'password': 'test_password',
            'role': 'user',
            'full_name': "User Name",
            'email_verified': True,
            'is_active': True,
            'joined_at': datetime.utcnow()
        }
        user = User(**user_data)
        self.session_test.add(user)
        self.session_test.commit()
        retrieved_user = self.user_controller.get_user_by_email(user.email)

        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.email, user.email)

    def test_update_user(self):
        user_data = {
            'email': 'contoller_update_user@example.com',
            'password': 'test_password',
            'role': 'user',
            'full_name': "User Name",
            'email_verified': True,
            'is_active': True,
            'joined_at': datetime.utcnow()
        }
        user = User(**user_data)
        self.session_test.add(user)
        self.session_test.commit()

        created_user = self.session_test.query(User).filter_by(email='contoller_update_user@example.com').first()
        created_user.email = 'contoller_update_user2@example.com'
        created_user.role = "developer"
        created_user.password = 'test2_password'
        created_user.full_name = "Dev Name"
        created_user.email_verified = False
        created_user.is_active = False
        self.user_controller.commit()
        updated_user = self.session_test.query(User).filter_by(email='contoller_update_user2@example.com').first()

        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.password, 'test2_password')
        self.assertEqual(updated_user.role, 'developer')
        self.assertEqual(updated_user.email_verified, False)
        self.assertEqual(updated_user.is_active, False)

    def test_email_exists(self):
        user_data = {
            'email': 'contoller_email_exists_user@example.com',
            'password': 'test_password',
            'role': 'user',
            'full_name': "User Name",
            'email_verified': True,
            'is_active': True,
            'joined_at': datetime.utcnow()
        }
        user = User(**user_data)
        self.session_test.add(user)
        self.session_test.commit()

        result = self.user_controller.email_exists("contoller_email_exists_user@example.com")
        self.assertIsInstance(result, bool)
        self.assertTrue(result)
        self.assertFalse(self.user_controller.email_exists("some_not_exists@gmail.com"))


if __name__ == '__main__':
    unittest.main()
