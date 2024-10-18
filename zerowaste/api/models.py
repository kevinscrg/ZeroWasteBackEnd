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


# Custom manager for CustomUser
# class UserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError(_("The Email field must be set"))
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)  # Hash the password
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError(_('Superuser must have is_staff=True.'))
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError(_('Superuser must have is_superuser=True.'))

#         return self.create_user(email, password, **extra_fields)


# AbstractBaseUser, PermissionsMixin
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

    
    # # Define custom related names for groups and user_permissions to avoid conflicts
    # groups = models.ManyToManyField(
    #     Group,
    #     related_name='customuser_set',  # Avoid conflict with auth.User.groups
    #     blank=True,
    #     help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
    #     verbose_name=_('groups'),
    # )
    
    # user_permissions = models.ManyToManyField(
    #     Permission,
    #     related_name='customuser_set',  # Avoid conflict with auth.User.user_permissions
    #     blank=True,
    #     help_text=_('Specific permissions for this user.'),
    #     verbose_name=_('user permissions'),
    # )

    # is_active = models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=False)
    # date_joined = models.DateTimeField(default=timezone.now)

    # objects = UserManager()  # Updated reference to UserManager

    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = []

    # class Meta:
    #     verbose_name = _('user')
    #     verbose_name_plural = _('users')

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
