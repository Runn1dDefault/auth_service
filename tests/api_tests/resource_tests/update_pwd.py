import unittest
from falcon import testing, status_codes

import api
from api.utils.hashers import get_hashed_password
from api.utils.tokens import auth_token_for_user, verify_token_for_user
from config import TOKEN_AUTH_HEADER
from dao.controllers import UserController
from dao.models import User
from dao.operations import initialize_models


class UpdatePasswordResourceTest(unittest.TestCase):
    def setUp(self):
        initialize_models()
        self.user_controller = UserController()

        self.api = testing.TestClient(api.create())
        self.api.app.add_route("/update_pwd", api.UpdatePasswordResource(api.VerifyEmailAuthMiddleware))
        self.api.app.add_route("/auth", api.AuthResource())

    def tearDown(self):
        self.user_controller.close()

    def test_success_update_password(self):
        test_user = User(
            email="success_verify_user@gmail.com",
            password=get_hashed_password("test_password"),
            role="user",
            full_name="Test User",
            email_verified=False
        )
        created = self.user_controller.create(test_user)
        self.assertTrue(created)

        verify_token = verify_token_for_user(test_user)
        response = self.api.simulate_post(
            '/update_pwd',
            json={'password': 'updatedPassword(2asd!'},
            headers={'X-VERIFY-TOKEN': f'{TOKEN_AUTH_HEADER} {verify_token}'}
        )
        self.assertEqual(status_codes.HTTP_OK, response.status, getattr(response, 'json', None))

        auth_resp = self.api.simulate_post(
            '/auth',
            json={"email": test_user.email, "password": "updatedPassword(2asd!"}
        )
        self.assertEqual(status_codes.HTTP_OK, auth_resp.status, getattr(response, 'json', None))
        self.assertIn('token', getattr(auth_resp, 'json'))

    def test_update_password_invalid_token(self):
        test_user = User(
            email="invalid_token_user@gmail.com",
            password=get_hashed_password("test_password"),
            role="user",
            full_name="Test User",
            email_verified=False
        )
        created = self.user_controller.create(test_user)
        self.assertTrue(created)

        response = self.api.simulate_post(
            '/update_pwd',
            json={'password': 'updatedPassword(2asd!'},
            headers={'X-VERIFY-TOKEN': f'{TOKEN_AUTH_HEADER} invalid_token'}
        )
        self.assertEqual(status_codes.HTTP_UNAUTHORIZED, response.status)

    def test_password_validate_errors(self):
        test_user = User(
            email="invalid_pwd_user@gmail.com",
            password=get_hashed_password("test_password"),
            role="user",
            full_name="Test User",
            email_verified=False
        )
        created = self.user_controller.create(test_user)
        self.assertTrue(created)

        verify_token = verify_token_for_user(test_user)
        response = self.api.simulate_post(
            '/update_pwd',
            json={'password': 'passwordonlyalpha'},
            headers={'X-VERIFY-TOKEN': f'{TOKEN_AUTH_HEADER} {verify_token}'}
        )
        self.assertEqual(status_codes.HTTP_BAD_REQUEST, response.status)
        response_data = getattr(response, 'json')
        self.assertIn('password', response_data)
        self.assertIsInstance(response_data['password'], list)

    def test_failure_invalid_verify_token(self):
        test_user = User(
            email="failure_invalid_verify_token_user@gmail.com",
            password=get_hashed_password("test_password"),
            role="user",
            full_name="Test User",
            email_verified=False
        )
        created = self.user_controller.create(test_user)
        self.assertTrue(created)

        response = self.api.simulate_post(
            '/update_pwd',
            json={'password': 'test_password'},
            headers={'X-VERIFY-TOKEN': f'{TOKEN_AUTH_HEADER} invalid_token'}
        )

        self.assertEqual(status_codes.HTTP_UNAUTHORIZED, response.status)

    def test_failure_with_auth_token(self):
        test_user = User(
            email="failure_with_auth_token_user@gmail.com",
            password=get_hashed_password("test_password"),
            role="user",
            full_name="Test User",
            email_verified=False
        )
        created = self.user_controller.create(test_user)
        self.assertTrue(created)

        token = auth_token_for_user(user=test_user)
        response = self.api.simulate_post(
            '/update_pwd',
            json={'password': 'someNewpassword12345dD'},
            headers={'X-VERIFY-TOKEN': f'{TOKEN_AUTH_HEADER} {token}'}
        )

        self.assertEqual(status_codes.HTTP_UNAUTHORIZED, response.status)

    def test_failure_with_auth_token_in_auth_header(self):
        test_user = User(
            email="failure_with_auth_token_in_auth_header_user@gmail.com",
            password=get_hashed_password("test_password"),
            role="user",
            full_name="Test User",
            email_verified=False
        )
        created = self.user_controller.create(test_user)
        self.assertTrue(created)

        token = auth_token_for_user(user=test_user)
        response = self.api.simulate_post(
            '/update_pwd',
            json={'password': 'someNewpassword12345dD'},
            headers={'Authorization': f'{TOKEN_AUTH_HEADER} {token}'}
        )

        self.assertEqual(status_codes.HTTP_UNAUTHORIZED, response.status)


if __name__ == '__main__':
    unittest.main()
