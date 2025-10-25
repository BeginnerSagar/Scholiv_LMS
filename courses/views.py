from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import School, Class, Subject, Lecture, Attendance
from .serializers import (
    SchoolSerializer,
    ClassSerializer,
    SubjectSerializer,
    LectureSerializer,
    AttendanceSerializer
)
from .permissions import IsAdminUser

# Create your views here.

class SchoolViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Admins to manage Schools.
    (Create, Read, Update, Delete)
    """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class ClassViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Admins to manage Classes.
    (Create, Read, Update, Delete)
    """
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class SubjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Admins to manage Subjects.
    (Create, Read, Update, Delete)
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class LectureViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Admins to manage Lectures.
    (Create, Read, Update, Delete)
    """
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Admins to manage Attendance records.
    (Create, Read, Update, Delete)
    
    Note: We will later create a separate endpoint for students
    to automatically mark their attendance. This is for manual admin management.
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

