from django.urls import path
from .views import signup, all_users, user_login, user_logout

from .views import UserRegistrationView, LoginAPIView, RefreshTokenAPIView

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('all-users/', all_users, name='all_users'),
    path('user-login/', user_login, name='user_login'),
    path('user-logout/', user_logout, name='user_logout'),

    path('api/register/', UserRegistrationView.as_view(), name='user-register'),
    path('api/login/', LoginAPIView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', RefreshTokenAPIView.as_view(), name='token_refresh'),
]