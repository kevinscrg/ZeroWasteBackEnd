from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
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
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('The user with this email address does not exist.')
          
        if user.check_password(password):
            return {
            'email': user.email,
            'tokens': user.tokens
            }
            
        raise AuthenticationFailed('The password is incorrect!')

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'preferred_notification_hour', 'preferences', 'allergies', 'saved_recipes']


    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with this email already exists!')
        return value
    

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
