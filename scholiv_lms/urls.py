"""
URL configuration for scholiv_lms project.
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. User App URLs
    path('api/users/', include('users.urls')),

    # 2. JWT Token Endpoints (for the frontend app)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 3. Admin Portal (Courses) App
    path('api/', include('courses.urls')),

    # 4. NEW: Browsable API Login
    # This is the new line that will add the "Log in"
    # button to the top-right corner of the page.
    path('api-auth/', include('rest_framework.urls')),
]

