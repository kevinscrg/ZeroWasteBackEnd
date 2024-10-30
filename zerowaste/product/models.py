from django.db import models
from api.models import User
class Product(models.Model):
    name = models.CharField(max_length=255)
    best_before = models.DateField()
    consumption_days = models.PositiveIntegerField(null=True, blank=True)
    opened = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class UserProductList(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)

    def __str__(self):
        return f"{self.owner.email}'s Product List"