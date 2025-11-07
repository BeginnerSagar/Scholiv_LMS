from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
# This is the correct place for all content-related ViewSets.
router = DefaultRouter()
router.register(r'schools', views.SchoolViewSet, basename='school')
router.register(r'classes', views.ClassViewSet, basename='class')
router.register(r'subjects', views.SubjectViewSet, basename='subject')
router.register(r'lectures', views.LectureViewSet, basename='lecture')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')

# --- Register the Q&A and Announcement ViewSets (Step 6.21) ---
router.register(r'announcements', views.AnnouncementViewSet, basename='announcement')
router.register(r'questions', views.QuestionViewSet, basename='question')
router.register(r'answers', views.AnswerViewSet, basename='answer')


# The API URLs are now determined automatically by the router.
# We also add our custom, non-router views (like file uploads)
urlpatterns = [
    # Custom path for attendance upload.
    # This must come *before* the router.urls to be matched correctly.
    path('attendance/upload/', views.AttendanceUploadView.as_view(), name='attendance-upload'),
    
    # Include all the router-generated URLs
    path('', include(router.urls)),
]