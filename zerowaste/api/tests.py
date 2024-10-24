from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Preference, Allergy, Recipe 

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
        self.user1 = User.objects.create(email="user1@example.com")
        self.user1.set_password("password123")
        self.user1.save()

        self.user2 = User.objects.create(email="user2@example.com")
        self.user2.set_password("password123")
        self.user2.save()

        self.delete_account_url_user1 = reverse('delete-account', kwargs={'user_id': self.user1.id})
        self.delete_account_url_user2 = reverse('delete-account', kwargs={'user_id': self.user2.id})

        response = self.client.post(reverse('login'), {'email': 'user1@example.com', 'password': 'password123'})
        self.user1_token = response.data['access']


    def test_delete_own_account(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user1_token)
        response = self.client.delete(self.delete_account_url_user1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user1.id).exists())
   
   
    def test_delete_other_user_account(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user1_token)
        response = self.client.delete(self.delete_account_url_user2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(User.objects.filter(id=self.user2.id).exists())


    def test_delete_without_authentication(self):
        response = self.client.delete(self.delete_account_url_user1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

