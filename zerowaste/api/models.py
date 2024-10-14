from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    preferred_notification_hour = models.IntegerField(null=True, blank=True)
    
    # Using JSONField to store lists and a map (dictionary)
    preferences = models.CharField(max_length=50, blank=True)  # List of strings
    allergies = models.CharField(max_length=50, blank=True)    # List of strings
    rated_recipes = models.JSONField(default=dict, blank=True)  # Map: recipe ID as key, rating as value
    saved_recipes = models.CharField(max_length=50, blank=True)  # List of saved recipe IDs (strings)

    def __str__(self):
        return self.email
