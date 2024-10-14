from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "preferred_notification_hour", "preferences", "allergies", "rated_recipes", "saved_recipes"]
        