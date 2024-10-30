from django.test import TestCase
from .models import Product
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Product, UserProductList
from rest_framework_simplejwt.tokens import RefreshToken

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

        # Create a UserProductList for the user
        self.user_product_list = UserProductList.objects.create(owner=self.user)
        self.user_product_list.products.add(self.product1)

    def authenticate(self):
        """Helper function to authenticate the user"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_user_product_list(self):
        self.authenticate()
        url = reverse('user-product-list')
        data = {
            "products": [
                {
                    "id": self.product1.id,
                    "name": self.product1.name,
                    "best_before": self.product1.best_before,
                    "consumption_days": self.product1.consumption_days,
                    "opened": self.product1.opened
                },
                {
                    "id": self.product2.id,
                    "name": self.product2.name,
                    "best_before": self.product2.best_before,
                    "consumption_days": self.product2.consumption_days,
                    "opened": self.product2.opened
                }
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserProductList.objects.count(), 2)  # Check if a new list is created

    def test_get_user_product_list(self):
        self.authenticate()
        url = reverse('user-product-list-detail', args=[self.user_product_list.id])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['products'][0]['name'], self.product1.name)

    def test_update_user_product_list(self):
        self.authenticate()
        url = reverse('user-product-list-detail', args=[self.user_product_list.id])
        data = {
            "products": [
                {
                    "id": self.product1.id,
                    "name": "Updated Apa Plata",
                    "best_before": "2024-12-31",
                    "consumption_days": 10,
                    "opened": "2024-01-01"
                }
            ]
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the update
        self.user_product_list.refresh_from_db()
        self.assertEqual(self.user_product_list.products.first().consumption_days, 10)

    def test_delete_user_product_list(self):
        self.authenticate()
        url = reverse('user-product-list-detail', args=[self.user_product_list.id])
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(UserProductList.objects.count(), 0)  # Verify the list has been deleted

    def test_unauthenticated_access(self):
        url = reverse('user-product-list')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



