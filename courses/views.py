from rest_framework import viewsets, permissions
from .models import School, Class, Subject, Lecture, Attendance
from .serializers import (
    SchoolSerializer, 
    ClassSerializer, 
    SubjectSerializer, 
    LectureSerializer, 
    AttendanceSerializer
)
# Import our NEW permission classes
from .permissions import IsSuperAdmin, IsSchoolAdmin, IsTeacher

# --- Core Management ViewSets (for Admins) ---

class SchoolViewSet(viewsets.ModelViewSet):
    """
    API endpoint for SuperAdmins to manage Schools.
    Only SuperAdmins can create, edit, or delete schools.
    """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    # Use our new permission: Only SuperAdmins
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class ClassViewSet(viewsets.ModelViewSet):
    """
    API endpoint for SchoolAdmins to manage Classes within their school.
    """
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    # Only School Admins (and SuperAdmins) can manage classes
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]
    
    # We will add logic here later to filter by the user's school

class SubjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for SchoolAdmins to manage Subjects.
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    # Only School Admins (and SuperAdmins) can manage subjects
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

class LectureViewSet(viewsets.ModelViewSet):
    """
    API endpoint for SuperAdmins to manage the master Lecture list.
    """
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    # Only SuperAdmins can upload/manage the core Scholive lectures
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Teachers (and Admins) to manage Attendance.
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    # Teachers and all Admins can manage attendance
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

