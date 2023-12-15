import unittest
import falcon
from falcon import testing

import api
from api.utils.hashers import get_hashed_password
from api.utils.tokens import encode_token, decode_token
from config import TOKEN_AUTH_HEADER
from dao.controllers import UserController
from dao.models import User
from dao.operations import initialize_models


class TestAuth(unittest.TestCase):
    def setUp(self):
        initialize_models()
        self.user_controller = UserController()

        self.api = testing.TestClient(api.create())
        self.api.app.add_route("/auth", api.AuthResource())
        self.api.app.add_route("/me-info", api.UserInfoResource())

    def tearDown(self):
        self.user_controller.close()

    def test_successful_authentication(self):
        test_user = User(
            email="auth_success_user@gmail.com",
            password=get_hashed_password("test_password"),
            role="user",
            full_name="Test User"
        )
        created = self.user_controller.create(test_user)
        self.assertTrue(created)

        response = self.api.simulate_post('/auth',
                                          json={'email': test_user.email, 'password': 'test_password'})

        self.assertEqual(response.status, falcon.HTTP_200)
        data = getattr(response, 'json')
        self.assertIn('token', data)

        token_data = decode_token(data["token"])
        self.assertIn('user_id', token_data)
        self.assertIn('user_email_verified', token_data)

        self.assertIn('user_role', response.cookies)
        self.assertIn('user_email_verified', response.cookies)

    def test_failed_authentication(self):
        test_user = User(
            email="auth_failed_user@gmail.com",
            password=get_hashed_password("test_password"),
            role="user",
            full_name="Test User"
        )
        created = self.user_controller.create(test_user)
        self.assertTrue(created)

        response = self.api.simulate_post('/auth',
                                          json={'email': test_user.email, 'password': 'wrong_password'})
        self.assertEqual(response.status, falcon.HTTP_UNAUTHORIZED)

    def test_successful_access_with_token(self):
        test_user = User(
            email="auth_successful_access_with_token_user@gmail.com",
            password=get_hashed_password("test_password"),
            role="user",
            full_name="Test User"
        )
        created = self.user_controller.create(test_user)
        self.assertTrue(created)

        token = encode_token({'user_id': test_user.id})
        headers = {'Authorization': f'{TOKEN_AUTH_HEADER} {token}'}
        response = self.api.simulate_get('/me-info', headers=headers)

        self.assertEqual(falcon.HTTP_OK, response.status, getattr(response, 'json'))

        data = getattr(response, 'json')
        self.assertIn("email", data)
        self.assertIn("full_name", data)

        self.assertEqual(data['email'], test_user.email)
        self.assertEqual(data['full_name'], test_user.full_name)

    def test_failed_access_without_token(self):
        response = self.api.simulate_get('/me-info')
        self.assertEqual(falcon.HTTP_UNAUTHORIZED, response.status)


if __name__ == '__main__':
    unittest.main()
