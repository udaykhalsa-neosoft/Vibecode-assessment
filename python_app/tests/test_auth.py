import json
from tests.base_test import BaseTestCase


class TestAuth(BaseTestCase):

    def test_register_user(self):
        """Test successful user registration."""
        response = self.client.post('/register', json={
            'username': 'johndoe',
            'email': 'john@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'User created', response.data)

    def test_register_duplicate_user(self):
        """Test registering a user that already exists."""
        payload = {'username': 'johndoe',
                   'email': 'john@example.com', 'password': 'password123'}
        self.client.post('/register', json=payload)

        # Attempt to register again
        response = self.client.post('/register', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'User already exists', response.data)

    def test_login_success(self):
        """Test successful login and token retrieval."""
        self.client.post('/register', json={
            'username': 'johndoe',
            'email': 'john@example.com',
            'password': 'password123'
        })

        response = self.client.post('/login', json={
            'username': 'johndoe',
            'password': 'password123'
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', data)

    def test_login_failure(self):
        """Test login with incorrect credentials."""
        response = self.client.post('/login', json={
            'username': 'wronguser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid credentials', response.data)

    def test_auth_blueprint_login(self):
        """Test the blueprint specific form-data login."""
        self.client.post('/register', json={
            'username': 'adminuser',
            'email': 'admin@example.com',
            'password': 'adminpass'
        })

        response = self.client.post('/auth/login', data={
            'username': 'adminuser',
            'password': 'adminpass'
        })
        self.assertEqual(response.status_code, 200)
