from django.urls import path
# Import the views from the current app's views.py
from . import views 

urlpatterns = [
    # Existing registration URL
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    
    # --- NEW URL FOR STEP 6.5 ---
    # This URL is for the School Admin to upload the student Excel file
    path('students/upload/', views.StudentUploadView.as_view(), name='student-upload'),
]
