from django.urls import path, include
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('user/', UserDetailView.as_view(), name='user-detail'),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('verify-email/', VerifyUserView.as_view(), name='verify-email'),
    path('change-list/', ChangeUserListView.as_view(), name='change-list'),
    path('collaborators/', GetCollaboratorsView.as_view(), name='list-collaborators'),
    path('user/update/preferred_notification_hour/<str:new_hour>/', PreferredNotificationHourUpdateView.as_view(),
         name='update-preferred-notification-hour'),
    path('user/update/preferences/', PreferencesUpdateView.as_view(), name='update-preferences'),
    path('user/update/allergies/', AllergiesUpdateView.as_view(), name='update-allergies'),
    path('user/update/notification_day/<int:new_day>/', NotificationDayUpdateView.as_view(),
         name='update-notification-day'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
