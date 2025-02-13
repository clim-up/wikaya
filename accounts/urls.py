from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView
from .views import GoogleLogin

urlpatterns = [
    path('google/login/', GoogleLogin.as_view(), name='google_login'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
]