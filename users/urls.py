from django.urls import path
from .views import UserRegistrationView

# This list defines the URL patterns for the 'users' app.
urlpatterns = [
    # When a request comes to 'register/', it will be handled by UserRegistrationView.
    path('register/', UserRegistrationView.as_view(), name='user-register'),
]

# from django.urls import path
# from .views import UserRegistrationView
# urlpathtterns = [
#     path('register/', UserRegistrationView.as_view(), name='user-register'),
# ]