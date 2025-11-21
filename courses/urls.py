from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .student_views import (
    StudentDashboardView,
    StudentLecturesView,
    StudentLectureDetailView,
    StudentAttendanceView,
    StudentProfileView,       # <--- New Import
    StudentChangePasswordView # <--- New Import
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'schools', views.SchoolViewSet, basename='school')
router.register(r'classes', views.ClassViewSet, basename='class')
router.register(r'subjects', views.SubjectViewSet, basename='subject')
router.register(r'lectures', views.LectureViewSet, basename='lecture')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')

# Register the Q&A System ViewSets
router.register(r'announcements', views.AnnouncementViewSet, basename='announcement')
router.register(r'questions', views.QuestionViewSet, basename='question')
router.register(r'answers', views.AnswerViewSet, basename='answer')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    
    # --- Student Portal URLs ---
    
    # 1. Dashboard
    path('student/dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
    
    # 2. Classroom
    path('student/lectures/', StudentLecturesView.as_view(), name='student-lectures'),
    path('student/lectures/<int:pk>/', StudentLectureDetailView.as_view(), name='student-lecture-detail'),
    
    # 3. Attendance
    path('student/attendance/', StudentAttendanceView.as_view(), name='student-attendance'),
    
    # 4. Profile & Security (NEW)
    path('student/profile/', StudentProfileView.as_view(), name='student-profile'),
    path('student/change-password/', StudentChangePasswordView.as_view(), name='student-change-password'),
]