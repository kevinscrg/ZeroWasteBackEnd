from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
from .models import User

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'preferred_notification_hour', 'preferences', 'allergies', 'saved_recipes']



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 
            'email', 
            'preferred_notification_hour', 
            'preferences', 
            'allergies', 
            'saved_recipes', 
            # 'is_active', 
            # 'is_staff', 
            # 'date_joined'
        ]
