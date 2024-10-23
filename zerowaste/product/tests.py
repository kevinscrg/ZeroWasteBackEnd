from django.test import TestCase
from .models import Product
from django.utils import timezone
from datetime import timedelta

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

