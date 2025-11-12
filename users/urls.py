from django.urls import path
from . import views

# This app_name is optional but good practice
app_name = 'users'

urlpatterns = [
    # Path for user registration
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    
    # Path for the SchoolAdmin to bulk upload students
    path('students/upload/', views.StudentUploadView.as_view(), name='student-upload'),
]