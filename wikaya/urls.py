from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('auth/allauth/', include('allauth.urls')),
    # path('auth/djrest', include('dj_rest_auth.urls')),
    path('auth/', include('dj_rest_auth.urls')),  
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('pages.urls')),
    # Endpoint to obtain a new access and refresh token pair
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Endpoint to refresh the access token using a refresh token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API schema in YAML format
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI (interactive API documentation)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # ReDoc UI (alternative API documentation)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]