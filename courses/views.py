from rest_framework import viewsets, permissions
from .models import School, Class, Subject, Lecture, Attendance, Announcement, Question, Answer
from .serializers import (
    SchoolSerializer, 
    ClassSerializer, 
    SubjectSerializer, 
    LectureSerializer, 
    AttendanceSerializer,
    AnnouncementSerializer,
    QuestionSerializer,
    AnswerSerializer
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


# ===========================
# NEW VIEWSETS FOR Q&A SYSTEM
# ===========================

class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Announcements.
    - Teachers and School Admins can create/edit/delete announcements
    - Students can only view announcements for their class
    """
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter announcements based on user role:
        - Teachers/Admins: See all announcements they posted
        - Students: See announcements for their assigned class
        """
        user = self.request.user
        
        # If SuperAdmin or School Admin, show all announcements
        if user.is_superuser or user.role in ['super_admin', 'school_admin']:
            return Announcement.objects.all()
        
        # If Teacher, show announcements they posted
        if user.role == 'teacher':
            return Announcement.objects.filter(posted_by=user)
        
        # If Student, show announcements for their class
        if user.role == 'student' and user.assigned_class:
            return Announcement.objects.filter(target_class=user.assigned_class)
        
        # Default: return empty queryset
        return Announcement.objects.none()
    
    def perform_create(self, serializer):
        """
        Automatically set the posted_by field when creating an announcement.
        """
        serializer.save(posted_by=self.request.user)


class QuestionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Questions.
    - Students can create questions about lectures
    - Teachers and Admins can view all questions
    - Everyone can view questions for lectures in their class
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter questions based on user role:
        - Teachers/Admins: See all questions
        - Students: See their own questions + questions from their class lectures
        """
        user = self.request.user
        
        # If SuperAdmin, School Admin, or Teacher, show all questions
        if user.is_superuser or user.role in ['super_admin', 'school_admin', 'teacher']:
            return Question.objects.all()
        
        # If Student, show questions for lectures in their class
        if user.role == 'student' and user.assigned_class:
            return Question.objects.filter(lecture__class_assigned=user.assigned_class)
        
        # Default: return empty queryset
        return Question.objects.none()
    
    def perform_create(self, serializer):
        """
        Automatically set the asked_by field when creating a question.
        """
        serializer.save(asked_by=self.request.user)


class AnswerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Answers.
    - Teachers can create answers to any question
    - Students can view answers but cannot create them
    """
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Everyone can see all answers (as long as they can see the question).
        """
        return Answer.objects.all()
    
    def perform_create(self, serializer):
        """
        Automatically set the answered_by field when creating an answer.
        Only Teachers and Admins can create answers.
        """
        user = self.request.user
        
        # Check if user is allowed to answer (Teacher or Admin)
        if user.role not in ['teacher', 'school_admin', 'super_admin'] and not user.is_superuser:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only teachers and admins can post answers.")
        
        serializer.save(answered_by=self.request.user)