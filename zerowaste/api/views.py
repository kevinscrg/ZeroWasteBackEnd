from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, UserRegistrationSerializer, UserSerializer
from rest_framework import generics, permissions
from .models import User


class LoginView(APIView):
    """
    API View to log in a user and return a JWT token.
    """
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']

            # Create tokens (access and refresh tokens)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Return both refresh and access token
            return Response({
                'refresh_token': str(refresh),
                'access_token': access_token,
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """
    API View to register a new user.
    """
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User registered successfully', 'email': user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
