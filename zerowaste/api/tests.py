from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import User, Preference, Allergy, Recipe 
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
        
        
        self.existing_email = 'admin@example.com'
        self.existing_password = 'strong_password'
        self.client.post(self.register_url, {
            'email': self.existing_email,
            'password': self.existing_password,
            'preferences': [self.preference1.id],  
            'allergies': [self.allergy1.id],      
            'saved_recipes': [self.recipe1.id]     
        }, format='json')
        

    def test_register_success(self):
       
        register_data = {
            'email': 'newuser@example.com',
            'password': 'strong_password',
            'preferences': [self.preference1.id],  
            'allergies': [self.allergy1.id],      
            'saved_recipes': [self.recipe1.id]     
        }

        response = self.client.post(self.register_url, register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], register_data['email'])
        self.assertNotIn('password', response.data)  
        self.assertTrue(User.objects.filter(email=register_data['email']).exists())

        user = User.objects.get(email=register_data['email'])
        self.assertEqual(list(user.preferences.all()), [self.preference1])
        self.assertEqual(list(user.allergies.all()), [self.allergy1])
        self.assertEqual(list(user.saved_recipes.all()), [self.recipe1])


    def test_register_duplicate_email(self):
        register_data = {
            'email': self.existing_email,  # Use the existing email
            'password': 'strong_password',
            'preferences': [self.preference1.id],  
            'allergies': [self.allergy1.id],      
            'saved_recipes': [self.recipe1.id]     
        }

        response = self.client.post(self.register_url, register_data, format='json')

  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  
        self.assertIn('email', response.data) 
        
        # TODO - solve error in tests.py, in the localhost it works, ma dau batuta
        # expected_error_message = "User with this email already exists!"
        # self.assertEqual(response.data['email'][0], expected_error_message)
        


    def test_register_invalid_data(self):
        register_data = {
            'password': 'password_without_email',
            'preferences': [],
            'allergies': [],
            'saved_recipes': []
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
            'preferences': [],
            'allergies': [],
            'saved_recipes': []
        }
        self.client.post(self.register_url, self.user_data, format='json')

    def test_login_success(self):
        # Test successful login
        response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
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
        
User = get_user_model()

class UserUpdateTests(TestCase):
    def setUp(self):
        # Create a test user
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
        url = reverse('update-preferred-notification-hour', kwargs={'new_hour': '14:30:00'})
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.preferred_notification_hour, time(14, 30))

    def test_update_preferences(self):
        # Assuming there are some preferences in the database
        preference_ids = [1]  # Replace with actual IDs from the setup
        url = reverse('update-preferences')
        response = self.client.patch(url, {'preferences': preference_ids}, format='json')

        # Check if response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_allergies(self):
        # Assuming there are some allergies in the database
        allergy_ids = [1]  # Replace with actual IDs from the setup
        url = reverse('update-allergies')
        response = self.client.patch(url, {'allergies': allergy_ids}, format='json')
        # Check if response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_notification_day(self):
        url = reverse('update-notification-day', kwargs={'new_day': 3})
        response = self.client.patch(url)

        # Check if response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)






