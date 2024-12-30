from django.urls import path
from .views import signup, all_users, user_login, user_logout

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('all-users/', all_users, name='all_users'),
    path('user-login/', user_login, name='user_login'),
    path('user-logout/', user_logout, name='user_logout'),
]