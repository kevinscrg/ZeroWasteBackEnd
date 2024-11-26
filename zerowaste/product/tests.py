from django.test import TestCase # type: ignore

from api.models import User
from .models import Product
from django.utils import timezone # type: ignore
from datetime import timedelta
from django.urls import reverse # type: ignore
from rest_framework import status # type: ignore
from rest_framework.test import APITestCase # type: ignore
from .models import Product
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from django.contrib.auth import get_user_model

User = get_user_model()


class ProductModelTest(TestCase):

    def setUp(self):
        # This method runs before each test, used to set up initial test data
        self.product = Product.objects.create(
            name="Produs de test",
            best_before=timezone.now() + timedelta(days=30),
            consumption_days=7,
            opened=timezone.now()
        )

    # Test Create Operation
    def test_create_product(self):
        product = Product.objects.create(
            name="Produs Nou",
            best_before=timezone.now() + timedelta(days=60),
            consumption_days=10
        )
        self.assertIsInstance(product, Product)
        self.assertEqual(product.name, "Produs Nou")
        self.assertEqual(Product.objects.count(), 2)  # Including product created in setUp

    # Test Read Operation
    def test_get_product(self):
        product = Product.objects.get(id=self.product.id)
        self.assertEqual(product.name, "Produs de test")
        self.assertEqual(product.consumption_days, 7)

    # Test Update Operation
    def test_update_product(self):
        product = Product.objects.get(id=self.product.id)
        product.name = "Updated Product Name"
        product.consumption_days = 14
        product.save()

        updated_product = Product.objects.get(id=self.product.id)
        self.assertEqual(updated_product.name, "Updated Product Name")
        self.assertEqual(updated_product.consumption_days, 14)
        self.assertNotEqual(updated_product.consumption_days, 7)

    # Test Delete Operation
    def test_delete_product(self):
        product = Product.objects.get(id=self.product.id)
        product.delete()

        # Assert that the product has been deleted
        self.assertEqual(Product.objects.count(), 0)

class UserProductListTests(APITestCase):
    
    def setUp(self):
        # Create a user
        self.user = User.objects.create(
            email='testuser@example.com',
            password='password'
        )
        self.token = RefreshToken.for_user(self.user).access_token

        # Create some products
        self.product1 = Product.objects.create(
            name="Apa Plata",
            best_before="2024-12-31",
            consumption_days=7,
            opened="2024-01-01"
        )
        self.product2 = Product.objects.create(
            name="Coca-Cola",
            best_before="2025-12-31",
            consumption_days=15,
            opened=None
        )
        
        response = self.client.post(reverse('login'), {'email': 'testuser@example.com', 'password': 'password'})
        acces = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + acces)
        
        # Create a UserProductList for the user
        self.client.post(reverse('verify-email'))
        
        self.user_product_list = User.objects.get(email = 'testuser@example.com').product_list
        self.user_product_list.products.add(self.product1)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + '')

    def authenticate(self):
        """Helper function to authenticate the user"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_user_product_list(self):
        self.authenticate()
        url = reverse('user-product-list')
        data = {
                "name": self.product2.name,
                "best_before": self.product2.best_before,
                "consumption_days": self.product2.consumption_days,
                "opened": self.product2.opened
            }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_unauthenticated_access(self):
        url = reverse('user-product-list')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



