import openpyxl  # <--- Added this for Excel
from django.contrib.auth import get_user_model # <--- Added this to find students
from rest_framework.parsers import MultiPartParser
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import School, Class, Subject, Lecture, Attendance, Announcement, Question, Answer
from .serializers import (
    SchoolSerializer, 
    ClassSerializer, 
    SubjectSerializer, 
    LectureSerializer, 
    AttendanceSerializer,
    AnnouncementSerializer,
    QuestionSerializer,
    AnswerSerializer,
    AttendanceUploadSerializer  
)
# Import our NEW permission classes
from .permissions import IsSuperAdmin, IsSchoolAdmin, IsTeacher

User = get_user_model()

# --- Core Management ViewSets (for Admins) ---

class SchoolViewSet(viewsets.ModelViewSet):
    """
    API endpoint for SuperAdmins to manage Schools.
    Only SuperAdmins can create, edit, or delete schools.
    """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class ClassViewSet(viewsets.ModelViewSet):
    """
    API endpoint for SchoolAdmins to manage Classes within their school.
    """
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

class SubjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for SchoolAdmins to manage Subjects.
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

class LectureViewSet(viewsets.ModelViewSet):
    """
    API endpoint for SuperAdmins to manage the master Lecture list.
    Includes video upload functionality.
    """
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    
    @action(detail=True, methods=['PUT'], parser_classes=[MultiPartParser])
    def upload_video(self, request, pk=None):
        """
        Custom endpoint to upload a video file for a specific lecture.
        URL: /api/lectures/{id}/upload_video/
        """
        lecture = self.get_object()
        video_file = request.FILES.get('video')
        
        if not video_file:
            return Response({'error': 'No video file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file type
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        file_extension = video_file.name.lower()[video_file.name.rfind('.'):]
        
        if file_extension not in allowed_extensions:
            return Response({'error': 'Invalid file type.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the video file
        lecture.video_file = video_file
        lecture.file_size_mb = round(video_file.size / (1024 * 1024), 2)
        lecture.save()
        
        return Response({
            'message': 'Video uploaded successfully!',
            'lecture_id': lecture.id,
            'video_url': lecture.get_video_url(),
        }, status=status.HTTP_200_OK)

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Teachers (and Admins) to manage Attendance.
    Includes Excel Upload for bulk attendance.
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    # UPDATE: Added 'GET' to methods list so the browser page loads
    @action(detail=False, methods=['GET', 'POST'], parser_classes=[MultiPartParser], serializer_class=AttendanceUploadSerializer)
    def upload(self, request):
        """
        Upload an Excel file (.xlsx) to mark attendance in bulk.
        URL: /api/attendance/upload/
        """
        # If the user just visits the page (GET), show a helpful message
        if request.method == 'GET':
            return Response({
                "message": "To upload attendance, please send a POST request with an Excel file.",
                "format": "Columns: A:Student Email, B:Lecture Title, C:Date"
            })

        # --- POST LOGIC (File Upload) ---
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        if not file_obj.name.endswith('.xlsx'):
            return Response({'error': 'File must be .xlsx format'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            wb = openpyxl.load_workbook(file_obj)
            ws = wb.active
            
            created_count = 0
            errors = []

            # Iterate starting from row 2 (skipping header)
            for index, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                email = row[0]
                lecture_title = row[1]
                date_val = row[2]

                if not email or not lecture_title or not date_val:
                    continue 

                # 1. Find Student
                try:
                    student = User.objects.get(email=email, role='student')
                except User.DoesNotExist:
                    errors.append(f"Row {index}: Student '{email}' not found.")
                    continue

                # 2. Find Lecture
                try:
                    lecture = Lecture.objects.get(title=lecture_title)
                except Lecture.DoesNotExist:
                    errors.append(f"Row {index}: Lecture '{lecture_title}' not found.")
                    continue

                # 3. Mark Present
                Attendance.objects.update_or_create(
                    student=student,
                    lecture=lecture,
                    date=date_val,
                    defaults={'present': True}
                )
                created_count += 1

            return Response({
                'message': f'Successfully marked attendance for {created_count} students.',
                'errors': errors
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ===========================
# Q&A SYSTEM VIEWSETS
# ===========================

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in ['super_admin', 'school_admin']:
            return Announcement.objects.all()
        if user.role == 'teacher':
            return Announcement.objects.filter(posted_by=user)
        if user.role == 'student' and user.assigned_class:
            return Announcement.objects.filter(target_class=user.assigned_class)
        return Announcement.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in ['super_admin', 'school_admin', 'teacher']:
            return Question.objects.all()
        if user.role == 'student' and user.assigned_class:
            return Question.objects.filter(lecture__class_assigned=user.assigned_class)
        return Question.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(asked_by=self.request.user)


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Answer.objects.all()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in ['teacher', 'school_admin', 'super_admin'] and not user.is_superuser:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only teachers and admins can post answers.")
        serializer.save(answered_by=self.request.user)