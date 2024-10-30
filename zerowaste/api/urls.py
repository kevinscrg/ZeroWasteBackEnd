from django.urls import path, include
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('user/', UserDetailView.as_view(), name='user-detail'),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('verify-email/', VerifyUserView.as_view(), name='verify-email'),
    path('change-list/', ChangeUserListView.as_view(), name='change-list'),
]
