from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
# The DefaultRouter automatically generates the URLs for our ViewSets
# (e.g., /schools/, /schools/<id>/)
router = DefaultRouter()
router.register(r'schools', views.SchoolViewSet, basename='school')
router.register(r'classes', views.ClassViewSet, basename='class')
router.register(r'subjects', views.SubjectViewSet, basename='subject')
router.register(r'lectures', views.LectureViewSet, basename='lecture')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')

# Register the NEW Q&A System ViewSets
router.register(r'announcements', views.AnnouncementViewSet, basename='announcement')
router.register(r'questions', views.QuestionViewSet, basename='question')
router.register(r'answers', views.AnswerViewSet, basename='answer')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]