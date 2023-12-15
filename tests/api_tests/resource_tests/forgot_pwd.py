import re
import unittest
from falcon import testing, status_codes

import api
from api.error_msgs import EMAIL_TTL_ERROR
from api.utils import verification_cache_key
from api.utils.hashers import get_hashed_password
from dao.connections import initialize_models, redis_scope
from dao.controllers import UserController
from dao.models import User


class ForgotPasswordResourceTest(unittest.TestCase):
    def setUp(self):
        initialize_models()
        self.user_controller = UserController()

        self.api = testing.TestClient(api.create())
        self.api.app.add_route("/forgot-pwd/{email}", api.ForgotPasswordResource())

    def tearDown(self):
        self.user_controller.close()

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
            f'/forgot-pwd/{test_user.email}',
            json={'password': 'test_password'},
        )
        self.assertEqual(status_codes.HTTP_400, response.status)

        exc_data = getattr(response, 'json')
        self.assertTrue(re.match(EMAIL_TTL_ERROR % r'\d+', exc_data['description']))

    def test_failed_on_not_exists_email(self):
        response = self.api.simulate_get('/verify/nonexistent@example.com')
        self.assertEqual(status_codes.HTTP_NOT_FOUND, response.status, getattr(response, 'json', None))


if __name__ == '__main__':
    unittest.main()
