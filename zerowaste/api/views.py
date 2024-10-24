from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer,LogoutSerializer, UserRegistrationSerializer, UserSerializer
from rest_framework import generics, permissions
from .models import User
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class LoginView(generics.CreateAPIView):
    """
    API View to log in a user and return a JWT token.
    """
    serializer_class = LoginSerializer
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        
        
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data["tokens"], status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    
class LogoutView(generics.GenericAPIView):
    """
    API View to log out a user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    

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
    
    

class DeleteAccountView(APIView):
    """
    API view to allow authenticated users to delete their own account.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user_to_delete = request.user
        
        if(user_to_delete.check_password(request.data["password"])):
            user_to_delete.delete()
            return Response({"detail": "Account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "wrong password"}, status=status.HTTP_401_UNAUTHORIZED)