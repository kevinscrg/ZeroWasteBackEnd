from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Preference, Allergy, Recipe 
from django.contrib.auth import get_user_model
from datetime import time

class UserLoginTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')   
        self.user_email = "admin@example.com"
        self.user_password = "root"

        self.user = User.objects.create(email=self.user_email)
        self.user.set_password(self.user_password)
        self.user.save() 

    def test_login_success(self):
        login_data = {
            'email': self.user_email,
            'password': self.user_password
        }
        
        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('access', response.data)  

    def test_login_invalid_credentials(self):
        # Attempt to login with wrong credentials
        login_data = {
            'email': self.user_email,
            'password': 'wrongpassword'
        }

        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'The password is incorrect!')
        
        
class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')   
        self.preference1 = Preference.objects.create(name='Preference1')
        self.allergy1 = Allergy.objects.create(name='Allergy1')
        self.recipe1 = Recipe.objects.create(name='Recipe1')
        self.existing_email = 'try@gmail.com'
        self.existing_password = 'strong_password'
        self.client.post(self.register_url, {
            'email': self.existing_email,
            'password': self.existing_password,
            'confirm_password': self.existing_password
        }, format='json')
        

    def test_register_success(self):
       
        register_data = {
            'email': 'newuser@example.com',
            'password': 'strong_password',
            'confirm_password': 'strong_password',
        }

        response = self.client.post(self.register_url, register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], register_data['email'])
        self.assertNotIn('password', response.data)  
        self.assertTrue(User.objects.filter(email=register_data['email']).exists())


    def test_register_duplicate_email(self):
        register_data = {
            'email': self.existing_email,  # Use the existing email
            'password': 'strong_password2',
            'confirm_password': 'strong_password2',
        }
        response = self.client.post(self.register_url, register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  
        self.assertIn('email', response.data) 
        
        
    def test_register_invalid_data(self):
        register_data = {
            'password': 'password_without_email',
        }
        response = self.client.post(self.register_url, register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
        
        
class UserLogoutTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')  
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
        }
        self.client.post(self.register_url, self.user_data, format='json')


    def test_login_success(self):
        # Test successful login
        response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'confirm_password': self.user_data['confirm_password']
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


    def test_logout_success(self):
        # Login to get tokens
        login_response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }, format='json')

        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']

        # Log out using the refresh token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)  
        logout_response = self.client.post(self.logout_url, {
            'refresh': refresh_token
        }, format='json')

        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)
        
        
class DeleteAccountTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(email="user@example.com")
        self.user.set_password("password123")
        self.user.save()
        response = self.client.post(reverse('login'), {'email': 'user@example.com', 'password': 'password123'})
        self.user_token = response.data['access']

    def test_delete_own_account(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        self.client.post(reverse("verify-email"))
        response = self.client.delete(reverse('delete-account'), data={'password': 'password123'})  
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_account_with_wrong_password(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        response = self.client.delete(reverse('delete-account'), data={'password': 'pass'})  
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(User.objects.filter(id=self.user.id).exists())
                                
    
    
    def test_delete_without_authentication(self):
        response = self.client.delete(reverse('delete-account'))  
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


User = get_user_model()

class UserUpdateTests(TestCase):
    def setUp(self):
        # Create a test user
        self.client = APIClient()
        self.user = User.objects.create(
            email='test@test.org',
            password='root'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create necessary allergy and preference records
        self.allergy = Allergy.objects.create(name="Peanut")
        self.preference = Preference.objects.create(name="Vegan")

    def test_update_preferred_notification_hour(self):
        # Ensure the URL matches the exact pattern defined
        url = reverse('update-preferred-notification-hour', kwargs={'new_hour': '14:30'})
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.preferred_notification_hour, time(14, 30))

    def test_update_preferences(self):
        # Assuming there are some preferences in the database
        preference_ids = ["Vegan"]  # Replace with actual IDs from the setup
        url = reverse('update-preferences')
        response = self.client.patch(url, {'preferences': preference_ids}, format='json')

        # Check if response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_allergies(self):
        # Assuming there are some allergies in the database
        allergy_ids = ["Peanut"]  # Replace with actual IDs from the setup
        url = reverse('update-allergies')
        response = self.client.patch(url, {'allergies': allergy_ids}, format='json')
        # Check if response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_notification_day(self):
        url = reverse('update-notification-day', kwargs={'new_day': 3})
        response = self.client.patch(url)

        # Check if response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class VerifyEmailViewTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        # Create a test user
        self.user = User.objects.create(
            email="testuser@example.com",
            password="password123"
        )
        
        # Generate a token for the user (assume this token is used in verification)
        response = self.client.post(reverse('login'), {'email': 'testuser@example.com', 'password': 'password123'})
        self.token = response.data['access']
        self.verify_url = reverse("verify-email")  # Replace with the actual name of your URL
    
    def test_verify_email_successful(self):
        """
        Ensure the email verification succeeds with a valid token.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.verify_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Email verified successfully.")
        # Additional checks (if the verification sets a flag on the user model)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)
    
    def test_verify_email_invalid_token(self):
        """
        Ensure the email verification fails with an invalid token.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + "invalidtoken" )
        response = self.client.post(self.verify_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_verify_email_already_verified(self):
        """
        Ensure the email verification fails if the email is already verified.
        """
        # Simulate an already verified email
        self.user.is_verified = True
        self.user.save()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.verify_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Email already verified.")

    def test_verify_email_invalid_request_method(self):
        """
        Ensure the email verification fails for unsupported HTTP methods.
        """
        response = self.client.get(self.verify_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
