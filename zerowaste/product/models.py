from django.db import models
class Product(models.Model):
    name = models.CharField(max_length=255)
    best_before = models.DateField()
    consumption_days = models.PositiveIntegerField(null=True, blank=True)
    opened = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class UserProductList(models.Model):
    share_code = models.CharField(max_length=6, unique=True)
    products = models.ManyToManyField(Product)

    def __str__(self):
        return self.share_code