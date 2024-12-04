# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager)
from product.models import UserProductList

# Create your custom models for Preferences, Allergies, and Recipe
class Preference(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Allergy(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    difficulty = models.IntegerField(null=True, blank=True)
    time = models.IntegerField(null=True, blank=True)
    recipe_type = models.CharField(max_length=255, null=True, blank=True)    

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):

    def create(self, email, password=None):
        if email is None:
            raise TypeError('Users should have an Email!')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser):
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    preferred_notification_hour = models.TimeField(blank=True, null=True)  # User's preferred notification hour
    preferences = models.ManyToManyField('Preference', related_name='users', blank=True)  # User's preferences
    allergies = models.ManyToManyField('Allergy', related_name='users', blank=True)  # User's allergies
    is_verified = models.BooleanField(default=False) # User's email verification status
    notification_day = models.IntegerField(default=1)  # User's preferred notification day's before expiry
    product_list = models.ForeignKey(UserProductList, on_delete=models.DO_NOTHING, blank=True, null=True)  # User's product list
    dark_mode = models.BooleanField(default=False)  # User's dark mode preference
    

    USERNAME_FIELD = 'email'
    
    
    objects = UserManager()
    
    def __str__(self):
        return self.email
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
    
# Through model for handling the recipe rating
class UserRecipeRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    rating = models.BooleanField()  # True for like, False for dislike
    class Meta:
        unique_together = ('user', 'recipe')  # Each user can rate each recipe once

    def __str__(self):
        return f'{self.user.email} rated {self.recipe.name} with {self.rating}'
