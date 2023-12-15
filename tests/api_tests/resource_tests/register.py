import unittest
import falcon
from falcon import testing

import api
from dao.connections import initialize_models
from dao.controllers import UserController


class RegisterTest(unittest.TestCase):
    def setUp(self):
        initialize_models()
        self.user_controller = UserController()

        self.api = testing.TestClient(api.create())
        self.api.app.add_route("/register", api.RegisterResource())

    def tearDown(self):
        self.user_controller.close()

    def test_successful_register(self):
        response = self.api.simulate_post(
            '/register',
            json={'email': 'user@gmail.com', 'password': 'somePassword123f}', 'full_name': 'New User'}
        )

        self.assertEqual(falcon.HTTP_OK, response.status, getattr(response, 'text', None))
        data = getattr(response, 'json')
        self.assertTrue(data['token'])

    def test_failed_register_missing_required_fields(self):
        response = self.api.simulate_post(
            '/register',
            json={'some_another_field': "blabla"}
        )

        self.assertEqual(falcon.HTTP_BAD_REQUEST, response.status)
        data = getattr(response, 'json')
        self.assertIn('email', data)
        self.assertIn('password', data)
        self.assertIn('full_name', data)

    def test_failed_register_with_wrong_email(self):
        payload_1 = {'email': 'testuser@example.com', 'password': 'somePassword123f}', 'full_name': 'New User'}
        response_1 = self.api.simulate_post('/register', json=payload_1)
        response_data = getattr(response_1, 'json')

        self.assertEqual(falcon.HTTP_BAD_REQUEST, response_1.status)
        self.assertIn('email', response_data)

        payload_2 = {'email': 'testuser@d', 'password': 'somePassword123f}', 'full_name': 'New User'}
        response_2 = self.api.simulate_post('/register', json=payload_2)

        self.assertEqual(falcon.HTTP_BAD_REQUEST, response_2.status)
        self.assertIn('email', response_data)

    def test_failed_register_with_empty_json(self):
        response = self.api.simulate_post('/register', json={})
        self.assertEqual(response.status, falcon.HTTP_BAD_REQUEST, getattr(response, 'text', None))


if __name__ == '__main__':
    unittest.main()
