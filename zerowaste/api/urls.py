from django.urls import path, include
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('user/', UserListView.as_view(), name='user-list'),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('products/', include('product.urls')),  
]
