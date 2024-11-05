import random
import string
from django.contrib.auth import authenticate # type: ignore
from rest_framework.exceptions import AuthenticationFailed # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken, TokenError # type: ignore
from rest_framework import serializers # type: ignore
from product.models import UserProductList
from .models import User

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
            return {
            'email': user.email,
            'tokens': user.tokens
            }
            
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
    class Meta:
        model = User
        fields = [
            'email', 
            'preferred_notification_hour', 
            'preferences', 
            'allergies', 
            'notification_day'
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