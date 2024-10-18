from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User

class UserLoginTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')  # Update with the correct login URL name
        self.user_email = "admin@exemple.com"
        self.user_password = "root"

        # Create a user for testing login
        self.user = User.objects.create(
            email=self.user_email,
            password=self.user_password
        )

    def test_login_success(self):
        # Define the payload for login
        login_data = {
            'email': self.user_email,
            'password': self.user_password
        }
        
        # Make a POST request to login
        response = self.client.post(self.login_url, login_data, format='json')

        # Check if the status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response contains the token (if token authentication is used)
        self.assertIn('token', response.data)  # Make sure token exists if you are using JWT or TokenAuth

    def test_login_invalid_credentials(self):
        # Attempt to login with wrong credentials
        login_data = {
            'email': self.user_email,
            'password': 'wrongpassword'
        }

        # Make a POST request to login
        response = self.client.post(self.login_url, login_data, format='json')

        # Check if the status code is 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Check if the response contains a 'detail' error message
        # self.assertIn('detail', response.data)
        # self.assertEqual(response.data['detail'], 'Invalid login credentials')
