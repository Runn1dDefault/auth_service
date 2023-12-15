import re
import unittest
from falcon import testing, status_codes

import api
from api.error_msgs import EMAIL_TTL_ERROR
from api.utils import verification_cache_key
from api.utils.hashers import get_hashed_password
from api.utils.tokens import auth_token_for_user, verify_token_for_user
from config import TOKEN_AUTH_HEADER
from dao.connections import redis_scope
from dao.controllers import UserController
from dao.models import User
from dao.operations import initialize_models


class VerifyEmailResourceTest(unittest.TestCase):
    def setUp(self):
        initialize_models()
        self.user_controller = UserController()

        self.api = testing.TestClient(api.create())
        self.api.app.add_route("/verify/{email}", api.VerifyEmailResource(api.VerifyEmailAuthMiddleware))

    def tearDown(self):
        self.user_controller.close()

    def test_success_verifying(self):
        test_user = User(
            email="success_verify_user@gmail.com",
            password=get_hashed_password("test_password"),
            role="user",
            full_name="Test User",
            email_verified=False
        )
        created = self.user_controller.create(test_user)
        self.assertTrue(created)

        cache_key = verification_cache_key(test_user.email)
        with redis_scope(0) as cache:
            cache.setex(cache_key, 5, "1")

        token = verify_token_for_user(user=test_user)

        response = self.api.simulate_post(
            f'/verify/{test_user.email}',
            json={'password': 'test_password'},
            headers={'X-VERIFY-TOKEN': f'{TOKEN_AUTH_HEADER} {token}'}
        )

        self.assertEqual(status_codes.HTTP_OK, response.status, getattr(response, 'json', ''))
        self.assertIn("user_email_verified", response.cookies)
        self.assertEqual("1", response.cookies.get("user_email_verified").value)

    def test_failure_ttl(self):
        test_user = User(
            email="failure_ttl_user@gmail.com",
            password=get_hashed_password("test_password"),
            role="user",
            full_name="Test User",
            email_verified=False
        )
        created = self.user_controller.create(test_user)
        self.assertTrue(created)

        cache_key = verification_cache_key(test_user.email)
        with redis_scope(0) as cache:
            cache.setex(cache_key, 5, "1")

        response = self.api.simulate_get(
            f'/verify/{test_user.email}',
            json={'password': 'test_password'},
        )
        self.assertEqual(status_codes.HTTP_400, response.status)

        exc_data = getattr(response, 'json')
        self.assertTrue(re.match(EMAIL_TTL_ERROR % r'\d+', exc_data['description']))

    def test_failed_on_not_exists_email(self):
        response = self.api.simulate_get('/verify/nonexistent@example.com')
        self.assertEqual(status_codes.HTTP_NOT_FOUND, response.status, getattr(response, 'json', None))

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
            f'/verify/{test_user.email}',
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
            f'/verify/{test_user.email}',
            json={'password': 'test_password'},
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
            f'/verify/{test_user.email}',
            json={'password': 'test_password'},
            headers={'Authorization': f'{TOKEN_AUTH_HEADER} {token}'}
        )

        self.assertEqual(status_codes.HTTP_UNAUTHORIZED, response.status)


if __name__ == '__main__':
    unittest.main()
