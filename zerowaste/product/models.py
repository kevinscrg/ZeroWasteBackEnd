from datetime import timedelta, date
from django.db import models # type: ignore
import random
import string

class Product(models.Model):
    name = models.CharField(max_length=255)
    best_before = models.DateField(null=True, blank=True)
    consumption_days = models.PositiveIntegerField(null=True, blank=True)
    opened = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    def calculate_opened_plus_consumption(self):
        if self.opened and self.consumption_days:
            return self.opened + timedelta(days=self.consumption_days)
        return None
    
    def is_expiring_soon(self, today, notification_day=1):
        expiration_date = None

        # Use best_before if available
        if self.best_before:
            expiration_date = self.best_before

        # Calculate expiration from opened + consumption_days if applicable
        if self.opened and self.consumption_days:
            opened_expiration = self.opened + timedelta(days=self.consumption_days)
            expiration_date = min(expiration_date, opened_expiration) if expiration_date else opened_expiration

        # If no expiration date is available, it's not expiring soon
        if not expiration_date:
            return False

        # Check if within the notification window
        return today <= expiration_date <= today + timedelta(days=notification_day)


class UserProductList(models.Model):
    share_code = models.CharField(max_length=6, unique=True) 
    products = models.ManyToManyField(Product)

    def __str__(self):
        return self.share_code
    
    def getExpiringProducts(self, notification_day):
        products = self.products.all()

        # Filter products with valid expiration dates
        valid_products = [
            product for product in products
            if product.best_before or (product.opened and product.consumption_days)
        ]

        # Sort by earliest expiration date
        products_sorted = sorted(
            valid_products,
            key=lambda product: (
                product.best_before or product.calculate_opened_plus_consumption() or date.max
            )
        )

        # Identify expiring products
        today = date.today()
        expiring_products = [
            product for product in products_sorted
            if product.is_expiring_soon(today, notification_day)
        ]

        return [product.name for product in expiring_products]
