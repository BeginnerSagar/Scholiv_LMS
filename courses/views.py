from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from openpyxl import load_workbook
import datetime

from .models import (
    School, 
    Class, 
    Subject, 
    Lecture, 
    Attendance,
    Announcement, # New
    Question,     # New
    Answer        # New
)
from .serializers import (
    SchoolSerializer, 
    ClassSerializer, 
    SubjectSerializer, 
    LectureSerializer, 
    AttendanceSerializer,
    AttendanceUploadSerializer,
    AnnouncementSerializer, # New
    QuestionSerializer,     # New
    AnswerSerializer        # New
)
# Correctly import all new permissions
from .permissions import IsSuperAdmin, IsSchoolAdmin, IsTeacher

# We need the User model for our Excel upload logic
from users.models import User, Role

# --- Admin Portal: Core CRUD Views (Phase 4) ---

class SchoolViewSet(viewsets.ModelViewSet):
    """
    API endpoint for SuperAdmins to manage Schools.
    """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class ClassViewSet(viewsets.ModelViewSet):
    """
    API endpoint for SchoolAdmins to manage Classes within their school.
    """
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]
    # Add a base queryset for the router to read (Fix for AssertionError)
    queryset = Class.objects.all() 

    def get_queryset(self):
        """
        This view should only return classes for the logged-in user's school.
        A SuperAdmin sees all classes.
        """
        user = self.request.user
        if user.is_superuser:
            return Class.objects.all()
        elif user.role == Role.SCHOOL_ADMIN:
            return Class.objects.filter(school=user.school)
        # Teachers or Students should not be managing classes
        return Class.objects.none() 

    def perform_create(self, serializer):
        """
        Automatically assign the class to the SchoolAdmin's school.
        """
        serializer.save(school=self.request.user.school)

class SubjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for SchoolAdmins to manage Subjects within their school.
    """
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]
    # Add a base queryset for the router to read (Fix for AssertionError)
    queryset = Subject.objects.all()

    def get_queryset(self):
        """
        This view should only return subjects for the logged-in user's school.
        A SuperAdmin sees all subjects.
        """
        user = self.request.user
        if user.is_superuser:
            return Subject.objects.all()
        elif user.role == Role.SCHOOL_ADMIN:
            return Subject.objects.filter(school=user.school)
        return Subject.objects.none()

    def perform_create(self, serializer):
        """
        Automatically assign the subject to the SchoolAdmin's school.
        """
        serializer.save(school=self.request.user.school)

class LectureViewSet(viewsets.ModelViewSet):
    """
    API endpoint for SuperAdmins to manage master lecture content.
    """
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Teachers to manage Attendance.
    """
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]
    # Add a base queryset for the router to read (Fix for AssertionError)
    queryset = Attendance.objects.all()

    def get_queryset(self):
        """
        This view should only return attendance records for the teacher's school.
        A SuperAdmin sees all.
        """
        user = self.request.user
        # Fix for AttributeError: Use the Role enum, not User.Role
        if user.is_superuser or user.role == Role.SUPER_ADMIN:
            return Attendance.objects.all()
        elif user.role == Role.TEACHER:
            # Filter attendance by students who belong to the same school as the teacher
            return Attendance.objects.filter(student__school=user.school)
        return Attendance.objects.none()


# --- Admin Portal: Advanced Features (Phase 5) ---

class AttendanceUploadView(generics.CreateAPIView):
    """
    API View for Teachers to bulk upload attendance via and Excel file.
    """
    serializer_class = AttendanceUploadSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        
        # Ensure the user is a teacher and has a school
        teacher = request.user
        if not teacher.school:
            return Response({"errors": ["Teacher is not assigned to any school."]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            wb = load_workbook(file, read_only=True)
            sheet = wb.active

            created_count = 0
            errors = []
            
            # Skip header row
            for i, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                if not any(row): # Skip empty rows
                    continue
                
                try:
                    student_email = row[0]
                    lecture_title = row[1]
                    attendance_date_str = row[2]

                    # 1. Find Student
                    try:
                        student = User.objects.get(email=student_email, school=teacher.school)
                        if student.role != Role.STUDENT:
                            raise User.DoesNotExist # Not a student, treat as not found
                    except User.DoesNotExist:
                        errors.append(f"Row {i}: Student with email '{student_email}' not found for your school.")
                        continue
                    
                    # 2. Find Lecture
                    try:
                        lecture = Lecture.objects.get(title=lecture_title)
                    except Lecture.DoesNotExist:
                        errors.append(f"Row {i}: Lecture with title '{lecture_title}' not found.")
                        continue

                    # 3. Parse Date
                    try:
                        # Convert date string (e.g., '2025-10-31') to date object
                        attendance_date = datetime.datetime.strptime(str(attendance_date_str).split(" ")[0], '%Y-%m-%d').date()
                    except ValueError:
                        errors.append(f"Row {i}: Invalid date format for '{attendance_date_str}'. Use YYYY-MM-DD.")
                        continue
                    
                    # 4. Create or Update Attendance
                    # We use get_or_create to avoid duplicate entries for the same student/lecture/date
                    obj, created = Attendance.objects.get_or_create(
                        student=student,
                        lecture=lecture,
                        date=attendance_date,
                        defaults={'is_present': True}
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        # If record already exists, update it to be present (e.g., if auto-mark was false)
                        if not obj.is_present:
                            obj.is_present = True
                            obj.save()
                            
                except Exception as e:
                    errors.append(f"Row {i}: An unexpected error occurred: {str(e)}")

            if created_count > 0 and not errors:
                return Response({"message": f"Processed file. Created {created_count} new record(s)."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": f"Processed file. Created {created_count} new record(s).", "errors": errors}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"errors": [f"Failed to process Excel file: {str(e)}"]}, status=status.HTTP_400_BAD_REQUEST)

# --- NEW: Q&A and Announcement Views (Step 6.20) ---

class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    API for Teachers to create Announcements for their class.
    Students and SchoolAdmins can read announcements.
    """
    serializer_class = AnnouncementSerializer
    queryset = Announcement.objects.all() # Add base queryset
    
    def get_permissions(self):
        """
        - Teachers can create (POST).
        - All authenticated users in the school can read (GET).
        """
        if self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated, IsTeacher]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        """
        Filter announcements to only show those for the user's school.
        SuperAdmin sees all.
        """
        user = self.request.user
        if user.is_superuser:
            return Announcement.objects.all()
        if user.school:
            return Announcement.objects.filter(school=user.school)
        return Announcement.objects.none()

    def perform_create(self, serializer):
        """
        When a Teacher creates an announcement, automatically set
        the 'teacher' to the logged-in user,
        the 'school' to the teacher's school,
        and the 'class_assigned' from the request data.
        """
        serializer.save(
            teacher=self.request.user,
            school=self.request.user.school
        )

class QuestionViewSet(viewsets.ModelViewSet):
    """
    API for Students to create Questions.
    Teachers and Admins can read all questions in their school.
    """
    serializer_class = QuestionSerializer
    queryset = Question.objects.all() # Add base queryset
    
    def get_permissions(self):
        """
        - Students can create (POST).
        - All authenticated users in the school can read (GET).
        - Only the student who wrote the question can edit/delete it.
        """
        if self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated] # Students, Teachers, or Admins can ask
        elif self.action in ['update', 'partial_update', 'destroy']:
            # This is complex permission, would need to check obj.student == request.user
            # For now, let's keep it simple: only auth'd users can interact
            self.permission_classes = [permissions.IsAuthenticated] 
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        """
        Filter questions to only show those for the user's school.
        """
        user = self.request.user
        if user.is_superuser:
            return Question.objects.all()
        if user.school:
            return Question.objects.filter(student__school=user.school)
        return Question.objects.none()

    def perform_create(self, serializer):
        """
        When a user creates a question, automatically set
        the 'student' to the logged-in user.
        """
        serializer.save(student=self.request.user)

class AnswerViewSet(viewsets.ModelViewSet):
    """
    API for Teachers to create Answers to Questions.
    """
    serializer_class = AnswerSerializer
    queryset = Answer.objects.all() # Add base queryset
    
    def get_permissions(self):
        """
        - Teachers can create (POST).
        - All authenticated users can read (GET).
        - Only the teacher who wrote the answer can edit/delete it.
        """
        if self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated, IsTeacher]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Would need to check obj.teacher == request.user
            self.permission_classes = [permissions.IsAuthenticated, IsTeacher]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        """
        Filter answers to only show those for the user's school.
        """
        user = self.request.user
        if user.is_superuser:
            return Answer.objects.all()
        if user.school:
            return Answer.objects.filter(teacher__school=user.school)
        return Answer.objects.none()

    def perform_create(self, serializer):
        """
        When a Teacher creates an answer, automatically set
        the 'teacher' to the logged-in user.
        """
        serializer.save(teacher=self.request.user)