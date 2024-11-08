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

class UserProductList(models.Model):
    share_code = models.CharField(max_length=6, unique=True) # we will use this code to share the product list with other users
    products = models.ManyToManyField(Product)

    def _generate_unique_code(self):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not UserProductList.objects.filter(share_code=code).exists():
                return code
            
    def __str__(self):
        return self.share_code