from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, UserRegistrationSerializer, UserSerializer
from rest_framework import generics, permissions
from .models import User


class LoginView(generics.CreateAPIView):
    """
    API View to log in a user and return a JWT token.
    """
    serializer_class = LoginSerializer
    def create(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.get(email = serializer.validated_data['email'])
        if user.check_password(serializer.validated_data['password']):

            # Create tokens (access and refresh tokens)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Return both refresh and access token
            return Response({
                'refresh_token': str(refresh),
                'access_token': access_token,
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class RegisterView(generics.CreateAPIView):
    """
    API View to register a new user.
    """
    serializer_class = UserRegistrationSerializer
      
    def create(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        preferences = serializer.validated_data['preferences']
        allergies = serializer.validated_data['allergies']
        saved_recipes = serializer.validated_data['saved_recipes']
        
        
        User.objects.create(
            email = serializer.validated_data["email"],
            password = "")
        user = User.objects.get(email=serializer.validated_data["email"])
        user.set_password(serializer.validated_data["password"])
        user.save()
        
        user.preferences.set(preferences)
        user.allergies.set(allergies)
        user.saved_recipes.set(saved_recipes)
        
        response_serializer = UserSerializer(User.objects.get(email=serializer.validated_data["email"]))
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


    


class UserListView(generics.ListCreateAPIView):
    """
    API view to retrieve list of users or create a new user.
    """
    queryset = User.objects.all()  # QuerySet for all users
    serializer_class = UserSerializer  # Serializer to handle User serialization
    permission_classes = [permissions.AllowAny]  

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to retrieve a list of users.
        """
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle POST request to create a new user.
        """
        return super().post(request, *args, **kwargs)
