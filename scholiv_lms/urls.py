"""
URL configuration for scholiv_lms project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# JWT Imports
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('users.urls')),
    path('api/', include('courses.urls')),

    # JWT Authentication Endpoints (For Postman/React/Mobile)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Browsable API Login/Logout (Adds the dropdown button in the browser)
    path('api-auth/', include('rest_framework.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)