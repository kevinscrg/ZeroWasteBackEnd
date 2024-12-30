from urllib.parse import urlparse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from zerowaste import settings
from .serializers import *
from .models import *
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from datetime import time
from product.models import UserProductList
from django.contrib.auth.tokens import default_token_generator  
from django.core.mail import send_mail
from rest_framework.exceptions import AuthenticationFailed
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.cache import cache
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Case, When


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
  
def send_verification_email(request, user):
        # Construct a generic verification URL
        token = default_token_generator.make_token(user)
        refer = request.META.get('HTTP_REFERER')
        parse_qsl = urlparse(refer)
        domain = f"{parse_qsl.scheme}://{parse_qsl.netloc}/"
        
        verification_url = f"{domain}successfully-created-account/?token={token}&uid={user.pk}"
        # Send email
        send_mail(
            subject='Verify your email',
            message=f"Hi, please click the link to verify your email: {verification_url} \n this email was generated automatically, please do not reply",
            from_email='zerowastenoreply@gmail.com',
            recipient_list=[user.email],
    )

class RegisterView(generics.CreateAPIView):
    """
    API View to register a new user.
    """
    serializer_class = UserRegistrationSerializer
      
    def create(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create the user
        user = User.objects.create(
            email=serializer.validated_data["email"]
        )
        user.set_password(serializer.validated_data["password"])  # Ensure password is hashed
        user.save()


        if settings.TESTING:
            user.is_verified = True
            sh_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            product_list = UserProductList.objects.create(share_code=sh_code)
            user.product_list = product_list
            user.save()
        else:
            # Trimite email-ul de verificare doar dacă nu e test
            send_verification_email(request, user)

        # Serialize the response
        response_serializer = UserSerializer(user)
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
            old_product_list = user_to_delete.product_list
            user_to_delete.delete()
            if User.objects.filter(product_list=old_product_list).count() == 0:
                for product in old_product_list.products.all():
                    product.delete()
                old_product_list.delete()
            return Response({"detail": "Account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Password is incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
    
class VerifyUserView(APIView):
    """
    API view to allow users to verify their email address.
    """
    
    def post(self, request):
        serializer = VerifyUserSerializer(data=request.data)
        
        if settings.TESTING:
            user = request.user
            if user.is_verified:
             return Response({"detail": "Email already verified."}, status=status.HTTP_200_OK)
            
            sh_code = serializer.generate_unique_share_code()
            product_list = UserProductList.objects.create(share_code=sh_code)
            user.product_list = product_list
            user.is_verified = True

            user.save()
            return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)

        token = request.data.get('token')
        uid = request.data.get('uid')
        
        user = User.objects.get(pk=uid)
        if not default_token_generator.check_token(user, token):
            raise AuthenticationFailed('The verify link is invalid') 

        if user.is_verified:
            return Response({"detail": "Email already verified."}, status=status.HTTP_200_OK)

        user.is_verified = True


        serializer.is_valid(raise_exception=True)

        sh_code = serializer.generate_unique_share_code()
        product_list = UserProductList.objects.create(share_code=sh_code)
        user.product_list = product_list

        user.save()

        return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)


    
class ChangeUserListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangeUserListSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            user = request.user
            old_product_list = user.product_list
            try:
                user.product_list = UserProductList.objects.get(share_code=serializer.validated_data["share_code"])
            except UserProductList.DoesNotExist:
                return Response({"detail": "Product list with provided share code does not exist."}, status=status.HTTP_404_NOT_FOUND)
            
            user.save()
            if User.objects.filter(product_list=old_product_list).count() == 0:
                for product in old_product_list.products.all():
                    product.delete()
                old_product_list.delete()
                
            return Response({"detail": "Product list updated successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetCollaboratorsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        product_list = user.product_list
        collaborators = User.objects.filter(product_list=product_list).exclude(id=user.id)
        serializer = CollaboratorSerializer(collaborators, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PreferredNotificationHourUpdateView(generics.UpdateAPIView):
    serializer_class = PreferredNotificationHourUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        new_hour = self.kwargs.get("new_hour")+":00"
        try:
            if "--" in new_hour:
                time_value = None
            else:
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
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        new_preferences_names = request.data.get("preferences", [])
        
        new_preferences = Preference.objects.filter(name__in=new_preferences_names)
        
        
        user = self.get_object()
        user.preferences.set(new_preferences)
        user.save()
        return Response({"preferences": [pref.id for pref in user.preferences.all()]},
                        status=status.HTTP_200_OK)

class AllergiesUpdateView(generics.UpdateAPIView):
    serializer_class = AllergiesUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        new_allergies_names = request.data.get("allergies", [])
        
        new_allergies = Allergy.objects.filter(name__in=new_allergies_names)
       
        
        user = self.get_object()
        user.allergies.set(new_allergies)
        user.save()
        return Response({"allergies": [allergy.id for allergy in user.allergies.all()]},
                        status=status.HTTP_200_OK)

class NotificationDayUpdateView(generics.UpdateAPIView):
    serializer_class = NotificationDayUpdateSerializer
    permission_classes = [IsAuthenticated]

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
        
        
class DarkModeUpdateView(generics.UpdateAPIView):
    serializer_class = DarkModeUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        user.dark_mode = not user.dark_mode
        user.save()

        return Response({"dark_mode": user.dark_mode},
                        status=status.HTTP_200_OK)

        
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    
class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed('A user with this email was not found.')
        
        token = default_token_generator.make_token(user)
        refer = request.META.get('HTTP_REFERER')
        parse_qsl = urlparse(refer)
        domain = f"{parse_qsl.scheme}://{parse_qsl.netloc}/"
        url = f"{domain}set-new-password/?token={token}&uid={user.pk}"
        send_mail(
            subject='Password Reset',
            message=f'Hi, please click the link to reset your password: {url}',
            from_email='zerowastenoreply@gmail.com',
            recipient_list=[user.email],)
        
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    def post(self, request):
        token = request.data.get('token')
        uid = request.data.get('uid')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        
        user = User.objects.get(pk=uid)
        
        if not default_token_generator.check_token(user, token):
            raise AuthenticationFailed('The reset link is invalid')
        
        if password != confirm_password:
            raise AuthenticationFailed('The passwords do not match')
        
        user.set_password(password)
        user.save()
        
        return Response({'success': 'Password reset successful'}, status=status.HTTP_200_OK)

class RecipePaginator(LimitOffsetPagination):
    default_limit = 10
    max_limit = 50

class RecipeListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = RecipePaginator
    
    def get(self, request):
       
        user = request.user
        
        if cache.get(f"recepies_{user.email}"):
            recipe_ids = cache.get(f"recepies_{user.email}")
            recipes = Recipe.objects.filter(id__in=recipe_ids).order_by(
                Case(*[When(id=pk, then=pos) for pos, pk in enumerate(recipe_ids)]))
            disliked_recipies_ids = UserRecipeRating.objects.filter(user=user, rating=False).values_list('recipe', flat=True)         
            recipes = recipes.exclude(id__in=disliked_recipies_ids)
            paginator = self.pagination_class()
            serializer = RecipeSerializer(paginator.paginate_queryset(recipes, request), many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        
        user_preferences = user.preferences.all()
        user_allergies = user.allergies.all()
        user_liked_recipes = list(UserRecipeRating.objects.filter(user=user, rating=True).values_list('recipe', flat=True))
        user_disliked_recipes = list(UserRecipeRating.objects.filter(user=user, rating=False).values_list('recipe', flat=True))
        
        product_list = user.product_list
        message = {
            'type': 'askScript',
            'message': {
                'Allergens': [allergy.name for allergy in user_allergies],
                'Preferences': [preference.name for preference in user_preferences],
                'Expiring Products' : product_list.getExpiringProducts(user.notification_day),
                'Liked Recipes' : user_liked_recipes,
                'Disliked Recipes' : user_disliked_recipes,
                'email': user.email
            }
        }
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "python_scripts",  
            message
            )

        return Response("ok", status=status.HTTP_200_OK)
    

    
class FilterRecipeView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = RecipePaginator

    def get(self, request):
        user = request.user
        cached_recipes = cache.get(f"recepies_{user.email}")
        
        time = request.query_params.get('filter[time]', None)
        recipe_type = request.query_params.get('filter[recipe_type]', None)
        difficulty = []
        favourites = request.query_params.get('filter[favourites]', None)
        if favourites is not None:
            if favourites not in ['true', 'false']:
                return Response({"detail": "Invalid favourites value."}, status=status.HTTP_400_BAD_REQUEST)
            favourites = True if favourites == 'true' else False
        for key, value in request.query_params.items():
            if key.startswith('filter[difficulty][') and key.endswith(']'):
                difficulty.append(value)

        if time is not None:
            try:
                time = int(time)
            except ValueError:
                return Response({"detail": "Invalid time value."}, status=status.HTTP_400_BAD_REQUEST)
            
        if favourites is not None:
            rated_recipe_ids = UserRecipeRating.objects.filter(user=user, rating=favourites).values_list('recipe', flat=True)
            recipes = Recipe.objects.filter(id__in=rated_recipe_ids)

        else:
            if not cached_recipes:
                return Response({"detail": "No recipes found."}, status=status.HTTP_404_NOT_FOUND)

            recipes = Recipe.objects.filter(id__in=cached_recipes)


        if recipe_type is not None:
            recipes = recipes.filter(recipe_type=recipe_type)

        if difficulty:
            recipes = recipes.filter(difficulty__in=difficulty)

        if time is not None:
            recipes = recipes.filter(time__lte=time)

        if not recipes.exists():
            return Response({"detail": "No recipes found."}, status=status.HTTP_404_NOT_FOUND)

        paginator = self.pagination_class()
        paginated_recipes = paginator.paginate_queryset(recipes, request)
        serializer = RecipeSerializer(paginated_recipes, many=True, context={'request': request})

        return paginator.get_paginated_response(serializer.data)
     
        
class RateRecipeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RateRecipeSerializer
    
    def post(self, request):
        user = request.user
        recipe_id = request.data.get('recipe_id')
        rating = request.data.get('rating')
        recipe = Recipe.objects.get(pk=recipe_id)
        
        if rating == None:
            if UserRecipeRating.objects.filter(user=user, recipe=recipe).exists():
                UserRecipeRating.objects.filter(user=user, recipe=recipe).delete()
                return Response({"detail": "Rating deleted successfully."}, status=status.HTTP_200_OK)
            return Response({"detail": "Rating does not exist."}, status=status.HTTP_200_OK)
        
        if UserRecipeRating.objects.filter(user=user, recipe=recipe).exists():
            UserRecipeRating.objects.filter(user=user, recipe=recipe).update(rating=rating)
            return Response({"detail": "Rating updated successfully."}, status=status.HTTP_200_OK)


        UserRecipeRating.objects.create(user=user, recipe=recipe, rating=rating)
        
        return Response({"detail": "Rating added successfully."}, status=status.HTTP_200_OK)
    
class SearchRecipeView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = RecipePaginator
    
    def get(self, request):
        user = request.user
        query = request.query_params.get('search', None)
        query = query.lower()
        cached_recipes = cache.get(f"recepies_{user.email}")
        if not cached_recipes:
            return Response({"detail": "No recipes found."}, status=status.HTTP_404_NOT_FOUND)
        
        if query is None:
            return Response({"detail": "No query provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        recipes = Recipe.objects.filter(id__in=cached_recipes)
        
        recipes = recipes.filter(name__icontains=query)
        if not recipes.exists():
            return Response({"detail": "No recipes found."}, status=status.HTTP_404_NOT_FOUND)
        
        paginator = self.pagination_class()
        paginated_recipes = paginator.paginate_queryset(recipes, request)
        serializer = RecipeSerializer(paginated_recipes, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)
    
class RefreshRecipeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user

        user_preferences = user.preferences.all()
        user_allergies = user.allergies.all()
        user_liked_recipes = list(UserRecipeRating.objects.filter(user=user, rating=True).values_list('recipe', flat=True))
        user_disliked_recipes = list(UserRecipeRating.objects.filter(user=user, rating=False).values_list('recipe', flat=True))
        
        product_list = user.product_list
        message = {
            'type': 'askScript',
            'message': {
                'Allergens': [allergy.name for allergy in user_allergies],
                'Preferences': [preference.name for preference in user_preferences],
                'Expiring Products' : product_list.getExpiringProducts(user.notification_day),
                'Liked Recipes' : user_liked_recipes,
                'Disliked Recipes' : user_disliked_recipes,
                'email': user.email
            }
        }
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "python_scripts",  
            message
            )

        return Response("ok", status=status.HTTP_200_OK)