# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

# Create your custom models for Preferences, Allergies, and Recipe
class Preference(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Allergy(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class User(models.Model):
    email = models.EmailField(_('email address'), unique=True)
    password = models.CharField(max_length=100)
    preferred_notification_hour = models.TimeField(default=timezone.now, blank=True)
    preferences = models.ManyToManyField('Preference', related_name='users', blank=True)  # User's preferences
    allergies = models.ManyToManyField('Allergy', related_name='users', blank=True)  # User's allergies
    saved_recipes = models.ManyToManyField('Recipe', related_name='saved_by_users', blank=True)  # User's saved recipes
    

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email
    
# Through model for handling the recipe rating
class UserRecipeRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    rating = models.IntegerField()

    class Meta:
        unique_together = ('user', 'recipe')  # Each user can rate each recipe once

    def __str__(self):
        return f'{self.user.email} rated {self.recipe.name} with {self.rating}'
