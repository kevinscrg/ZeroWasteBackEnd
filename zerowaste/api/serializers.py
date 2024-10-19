from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
from .models import User

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    tokens = serializers.SerializerMethodField()
    
    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
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
        
        user = User.objects.get(email=email)
        
        if user.check_password(password):
            
            return {
            'tokens': user.tokens
            }
            
        return super().validate(data)

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
        ]
