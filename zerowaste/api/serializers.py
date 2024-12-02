import random
import string
from django.contrib.auth import authenticate, get_user_model # type: ignore
from rest_framework.exceptions import AuthenticationFailed # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken, TokenError # type: ignore
from rest_framework import serializers # type: ignore
from product.models import UserProductList
from zerowaste import settings
from .models import *

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    tokens = serializers.SerializerMethodField()
        
    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])

        return {
            'access': user.tokens()['access'],
            'refresh': user.tokens()['refresh']
        }   
        
    class Meta:
        model = User
        fields = ['email', 'password', 'tokens']

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        
        if email is None:
            raise AuthenticationFailed('An email address is required to log in.')
        if password is None:
            raise AuthenticationFailed('A password is required to log in.')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('The user with this email address does not exist.')
          
        if user.check_password(password):
            if settings.TESTING:
                return {
                'email': user.email,
                'tokens': user.tokens
                }
            elif user.is_verified:
                return {
                'email': user.email,
                'tokens': user.tokens
                }
            raise AuthenticationFailed('The email is not verified!')
        raise AuthenticationFailed('The password is incorrect!')

class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password']


    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with this email already exists!')
        return value
    
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Passwords do not match!')
        self.validate_email(data['email'])
        return data
    

class UserSerializer(serializers.ModelSerializer):
    preferences = serializers.SerializerMethodField()
    allergies = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 
            'preferred_notification_hour', 
            'preferences', 
            'allergies', 
            'notification_day',
            'dark_mode'
        ]

    def get_preferences(self, obj):
        # Devuelve una lista de nombres de preferencias
        return [preference.name for preference in obj.preferences.all()]

    def get_allergies(self, obj):
        # Devuelve una lista de nombres de alergias
        return [allergy.name for allergy in obj.allergies.all()]
        
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')       


class VerifyUserSerializer(serializers.Serializer):
    def generate_unique_share_code(self):
        while True:
            share_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not UserProductList.objects.filter(share_code=share_code).exists():
                return share_code
            
            
class ChangeUserListSerializer(serializers.Serializer):
    share_code = serializers.CharField()
    
    def validate_share_code(self, value):
        if not UserProductList.objects.filter(share_code=value).exists():
            raise serializers.ValidationError('Invalid share code!')
        return value
    
    
class CollaboratorSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with this email does not exist!')
        return value

class PreferredNotificationHourUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['preferred_notification_hour']

class PreferencesUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['preferences']

class AllergiesUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['allergies']

class NotificationDayUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['notification_day']
        
        
class DarkModeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['dark_mode']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, data):
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        if new_password != confirm_password:
            raise serializers.ValidationError("New passwords do not match.")
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user       
      

class RecipeSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'link', 'name', 'image', 'recipe_type', 'difficulty', 'time', 'rating']

    def get_rating(self, obj):
        user = self.context['request'].user
        rating = UserRecipeRating.objects.filter(user=user, recipe=obj).first()
        return rating.rating if rating else None


class RateRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRecipeRating
        fields = ['recipe', 'rating']