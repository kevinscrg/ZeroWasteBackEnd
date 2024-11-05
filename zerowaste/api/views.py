from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions
from .models import User
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    LoginSerializer,
    LogoutSerializer, 
    UserRegistrationSerializer, 
    UserSerializer,
    PreferredNotificationHourUpdateSerializer,
    PreferencesUpdateSerializer,
    AllergiesUpdateSerializer,
    NotificationDayUpdateSerializer,
)
from datetime import time


class LoginView(generics.CreateAPIView):
    """
    API View to log in a user and return a JWT token.
    """
    serializer_class = LoginSerializer
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        
        print(request.data)
        
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data["tokens"], status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    
class LogoutView(generics.GenericAPIView):
    """
    API View to log out a user.
    """
    serializer_class = LogoutSerializer

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
  
    
class RegisterView(generics.CreateAPIView):
    """
    API View to register a new user.
    """
    serializer_class = UserRegistrationSerializer
      
    def create(self, request, *args, **kwargs):
        
        
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        User.objects.create(
            email = serializer.validated_data["email"],
            password = serializer.validated_data["password"])
        
        

        
        response_serializer = UserSerializer(User.objects.get(email=serializer.validated_data["email"]))
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class UserListView(generics.ListAPIView):
    """
    API view to retrieve list of users
    """
    queryset = User.objects.all()  
    serializer_class = UserSerializer  
    permission_classes = [permissions.AllowAny]  
    

class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request):
        serializer = UserSerializer(self.get_object())
        return Response(serializer.data)

class PreferredNotificationHourUpdateView(generics.UpdateAPIView):
    serializer_class = PreferredNotificationHourUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        new_hour = self.kwargs.get("new_hour")
        try:
            hour, minute, second = map(int, new_hour.split(":"))
            time_value = time(hour, minute, second)
        except ValueError:
            return Response({"error": "Invalid time format. Use HH:MM:SS."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = self.get_object()
        user.preferred_notification_hour = time_value
        user.save()

        return Response({"preferred_notification_hour": user.preferred_notification_hour},
                        status=status.HTTP_200_OK)

class PreferencesUpdateView(generics.UpdateAPIView):
    serializer_class = PreferencesUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        new_preferences = request.data.get("preferences", [])
        user = self.get_object()
        user.preferences.set(new_preferences)
        user.save()
        return Response({"preferences": [pref.id for pref in user.preferences.all()]},
                        status=status.HTTP_200_OK)

class AllergiesUpdateView(generics.UpdateAPIView):
    serializer_class = AllergiesUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        new_allergies = request.data.get("allergies", [])
        user = self.get_object()
        user.allergies.set(new_allergies)
        user.save()
        return Response({"allergies": [allergy.id for allergy in user.allergies.all()]},
                        status=status.HTTP_200_OK)

class NotificationDayUpdateView(generics.UpdateAPIView):
    serializer_class = NotificationDayUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        new_day = self.kwargs.get("new_day")
        try:
            day_value = int(new_day)
            if day_value < 0:
                raise ValueError("Day must be a positive integer.")
        except ValueError:
            return Response({"error": "Invalid day. Provide a positive integer."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = self.get_object()
        user.notification_day = day_value
        user.save()

        return Response({"notification_day": user.notification_day},
                        status=status.HTTP_200_OK)