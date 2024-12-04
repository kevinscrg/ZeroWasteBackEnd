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
    
    def is_expiring_soon(product, today, notification_day=1):
    
        expiration_date = None

        if product.best_before:
            expiration_date = product.best_before

        if product.opened and product.consumption_days:
            opened_expiration = product.opened + timedelta(days=product.consumption_days)
           
            if expiration_date:
                expiration_date = min(expiration_date, opened_expiration)
            else:
                expiration_date = opened_expiration


        if not expiration_date:
            return False

        return today <= expiration_date <= today + timedelta(days=notification_day)

class UserProductList(models.Model):
    share_code = models.CharField(max_length=6, unique=True) 
    products = models.ManyToManyField(Product)

    def __str__(self):
        return self.share_code
    
    def getExpiringProducts(self, notification_day):
        products = self.products.all()
        
        valid_products = [
            product for product in products
            if product.best_before or (product.opened and product.consumption_days)
        ]
        
        products_sorted = sorted(
            valid_products,
            key=lambda product: (
                product.best_before or date.max,  
                product.calculate_opened_plus_consumption() or product.best_before  
            )
        )        
        return [product.name for product in products_sorted if product.best_before and product.is_expiring_soon(date.today(), notification_day)]