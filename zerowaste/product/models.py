from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    best_before = models.DateField()
    consumption_days = models.PositiveIntegerField()
    opened = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
