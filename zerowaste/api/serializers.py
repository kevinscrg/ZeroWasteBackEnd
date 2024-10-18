from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
from .models import User

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise AuthenticationFailed('Invalid login credentials')

            if not user.is_active:
                raise AuthenticationFailed('User is deactivated')

        else:
            raise serializers.ValidationError('Both "email" and "password" are required.')

        data['user'] = user
        return data
    

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'preferred_notification_hour', 'preferences', 'allergies', 'saved_recipes']

    def create(self, validated_data):
        preferences = validated_data.pop('preferences', [])
        allergies = validated_data.pop('allergies', [])
        saved_recipes = validated_data.pop('saved_recipes', [])
        
        user = User(**validated_data)
        user.set_password(validated_data['password'])  # Hash the password
        user.save()

        # Handle preferences, allergies, and saved recipes
        user.preferences.set(preferences)
        user.allergies.set(allergies)
        user.saved_recipes.set(saved_recipes)

        return user
    


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
            'is_active', 
            'is_staff', 
            'date_joined'
        ]
