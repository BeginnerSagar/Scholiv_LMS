from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .serializers import ChangePasswordSerializer
from .models import Lecture, Attendance, Announcement, Subject
from users.models import Role


class IsStudent(IsAuthenticated):
    """
    Custom permission that only allows students to access.
    """
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        if not is_authenticated:
            return False
        return request.user.role == Role.STUDENT or request.user.is_superuser


class StudentDashboardView(APIView):
    """
    API endpoint that returns a student's dashboard summary.
    URL: /api/student/dashboard/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role != Role.STUDENT and not user.is_superuser:
            return Response(
                {"error": "This endpoint is only for students."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not user.assigned_class and not user.is_superuser:
            return Response(
                {"error": "You are not assigned to any class. Please contact your school admin."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        student_class = user.assigned_class
        
        # Calculate Attendance Statistics
        total_attendance_records = Attendance.objects.filter(student=user).count()
        present_count = Attendance.objects.filter(student=user, present=True).count()
        
        if total_attendance_records > 0:
            attendance_percentage = round((present_count / total_attendance_records) * 100, 1)
        else:
            attendance_percentage = 0.0
        
        # Get Lectures for Student's Class
        if student_class:
            lectures = Lecture.objects.filter(class_assigned=student_class).order_by('-uploaded_at')
            total_lectures = lectures.count()
            recent_lectures = lectures[:5]
        else:
            total_lectures = 0
            recent_lectures = []
        
        # Get Announcements for Student's Class
        if student_class:
            announcements = Announcement.objects.filter(target_class=student_class).order_by('-created_at')
            one_week_ago = timezone.now() - timedelta(days=7)
            new_announcements_count = announcements.filter(created_at__gte=one_week_ago).count()
            recent_announcements = announcements[:3]
        else:
            new_announcements_count = 0
            recent_announcements = []
        
        response_data = {
            "student": {
                "id": user.id,
                "username": user.username,
                "full_name": f"{user.first_name} {user.last_name}".strip() or user.username,
                "email": user.email,
                "class_name": student_class.name if student_class else None,
                "school_name": user.school.name if user.school else None,
            },
            "attendance": {
                "percentage": attendance_percentage,
                "total_records": total_attendance_records,
                "present_count": present_count,
                "absent_count": total_attendance_records - present_count,
            },
            "lectures": {
                "total_count": total_lectures,
                "recent": [
                    {
                        "id": lecture.id,
                        "title": lecture.title,
                        "subject": lecture.subject.name if lecture.subject else None,
                        "topic": lecture.topic,
                        "uploaded_at": lecture.uploaded_at,
                        "has_video": bool(lecture.video_file or lecture.video_url),
                    }
                    for lecture in recent_lectures
                ]
            },
            "announcements": {
                "new_count": new_announcements_count,
                "recent": [
                    {
                        "id": announcement.id,
                        "title": announcement.title,
                        "content": announcement.content[:100] + "..." if announcement.content and len(announcement.content) > 100 else announcement.content,
                        "priority": announcement.priority,
                        "posted_by": announcement.posted_by.username,
                        "created_at": announcement.created_at,
                    }
                    for announcement in recent_announcements
                ]
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


# ===========================
# STEP 2: MY LECTURES API
# ===========================

class StudentLecturesView(APIView):
    """
    API endpoint for students to view lectures assigned to their class.
    URL: /api/student/lectures/
    
    Query Parameters:
    - subject: Filter by subject ID (e.g., ?subject=1)
    - search: Search by title or topic (e.g., ?search=algebra)
    
    Returns:
    - List of subjects with their lectures
    - OR filtered lectures if query params are provided
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Verify user is a student
        if user.role != Role.STUDENT and not user.is_superuser:
            return Response(
                {"error": "This endpoint is only for students."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if student has an assigned class
        if not user.assigned_class and not user.is_superuser:
            return Response(
                {"error": "You are not assigned to any class."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        student_class = user.assigned_class
        
        # Get query parameters
        subject_id = request.query_params.get('subject', None)
        search_query = request.query_params.get('search', None)
        
        # Base queryset - only lectures for student's class
        lectures = Lecture.objects.filter(
            class_assigned=student_class
        ).select_related('subject').order_by('-uploaded_at')
        
        # Filter by subject if provided
        if subject_id:
            lectures = lectures.filter(subject_id=subject_id)
        
        # Search by title or topic if provided
        if search_query:
            lectures = lectures.filter(
                Q(title__icontains=search_query) |
                Q(topic__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Get student's watched lectures for marking
        watched_lecture_ids = Attendance.objects.filter(
            student=user,
            watched_video=True
        ).values_list('lecture_id', flat=True)
        
        # Build lecture list with watch status
        lecture_list = []
        for lecture in lectures:
            lecture_data = {
                "id": lecture.id,
                "title": lecture.title,
                "description": lecture.description,
                "subject": {
                    "id": lecture.subject.id if lecture.subject else None,
                    "name": lecture.subject.name if lecture.subject else "No Subject"
                },
                "topic": lecture.topic,
                "duration_minutes": lecture.duration_minutes,
                "has_video": bool(lecture.video_file or lecture.video_url),
                "video_url": lecture.get_video_url() if lecture.video_file or lecture.video_url else None,
                "uploaded_at": lecture.uploaded_at,
                "is_watched": lecture.id in watched_lecture_ids,
            }
            lecture_list.append(lecture_data)
        
        # Get list of subjects available for this class (for filter dropdown)
        available_subjects = Subject.objects.filter(
            lectures__class_assigned=student_class
        ).distinct()
        
        subject_list = [
            {"id": subj.id, "name": subj.name}
            for subj in available_subjects
        ]
        
        response_data = {
            "class_name": student_class.name if student_class else None,
            "total_lectures": len(lecture_list),
            "watched_count": len([l for l in lecture_list if l['is_watched']]),
            "available_subjects": subject_list,
            "lectures": lecture_list,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class StudentLectureDetailView(APIView):
    """
    API endpoint for students to view a single lecture's details.
    URL: /api/student/lectures/<id>/
    
    Returns:
    - Full lecture details including video URL
    - Related questions for this lecture
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        user = request.user
        
        # Verify user is a student
        if user.role != Role.STUDENT and not user.is_superuser:
            return Response(
                {"error": "This endpoint is only for students."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get the lecture
        try:
            lecture = Lecture.objects.select_related('subject', 'class_assigned').get(pk=pk)
        except Lecture.DoesNotExist:
            return Response(
                {"error": "Lecture not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify lecture is for student's class
        if user.assigned_class and lecture.class_assigned != user.assigned_class:
            return Response(
                {"error": "You don't have access to this lecture."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if student has watched this lecture
        is_watched = Attendance.objects.filter(
            student=user,
            lecture=lecture,
            watched_video=True
        ).exists()
        
        # Get questions for this lecture
        questions = lecture.questions.all().order_by('-created_at')[:5]
        
        response_data = {
            "id": lecture.id,
            "title": lecture.title,
            "description": lecture.description,
            "subject": {
                "id": lecture.subject.id if lecture.subject else None,
                "name": lecture.subject.name if lecture.subject else None
            },
            "class_name": lecture.class_assigned.name if lecture.class_assigned else None,
            "topic": lecture.topic,
            "duration_minutes": lecture.duration_minutes,
            "video_url": lecture.get_video_url(),
            "has_video": bool(lecture.video_file or lecture.video_url),
            "uploaded_at": lecture.uploaded_at,
            "is_watched": is_watched,
            "recent_questions": [
                {
                    "id": q.id,
                    "title": q.title,
                    "asked_by": q.asked_by.username,
                    "is_answered": q.is_answered,
                    "created_at": q.created_at,
                }
                for q in questions
            ],
            "question_count": lecture.questions.count(),
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    # ... (Keep all previous code) ...

# ===========================
# STEP 3: MY ATTENDANCE API (NEW!)
# ===========================

class StudentAttendanceView(APIView):
    """
    API endpoint for students to view their detailed attendance history.
    URL: /api/student/attendance/
    Query Params: ?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        user = request.user
        
        # 1. Base Query: Get all attendance records for this student
        queryset = Attendance.objects.filter(student=user).select_related('lecture').order_by('-date')

        # 2. Date Filtering (Optional)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # 3. Calculate Summary Stats (for the filtered period)
        total_records = queryset.count()
        present_count = queryset.filter(present=True).count()
        absent_count = total_records - present_count
        
        percentage = 0
        if total_records > 0:
            percentage = round((present_count / total_records) * 100, 2)

        # 4. Build History List
        history = []
        for record in queryset:
            history.append({
                "id": record.id,
                "date": record.date,
                "lecture_title": record.lecture.title if record.lecture else "N/A",
                "status": "Present" if record.present else "Absent",
                "color": "green" if record.present else "red" # Helper for frontend UI
            })

        response_data = {
            "summary": {
                "total_lectures": total_records,
                "present": present_count,
                "absent": absent_count,
                "percentage": f"{percentage}%"
            },
            "history": history
        }

        return Response(response_data, status=status.HTTP_200_OK)
 
# ===========================
# STEP 4: PROFILE & SECURITY
# ===========================

class StudentProfileView(APIView):
    """
    API endpoint for students to view their profile details.
    URL: /api/student/profile/
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        user = request.user
        
        data = {
            "id": user.id,
            "username": user.username,
            "full_name": f"{user.first_name} {user.last_name}".strip(),
            "email": user.email,
            "role": "Student",
            "school": user.school.name if user.school else "N/A",
            "assigned_class": user.assigned_class.name if user.assigned_class else "N/A",
            "date_joined": user.date_joined.strftime("%Y-%m-%d"),
        }
        return Response(data, status=status.HTTP_200_OK)


class StudentChangePasswordView(APIView):
    """
    API endpoint for students to change their password.
    URL: /api/student/change-password/
    """
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = ChangePasswordSerializer  # <--- This line generates the UI Form!

    # 1. Handle Browser Visit
    def get(self, request):
        return Response({
            "message": "To change your password, please use the form below.",
        }, status=status.HTTP_200_OK)

    # 2. Handle Password Change
    def post(self, request):
        # Load data into serializer
        serializer = self.serializer_class(data=request.data)
        
        # Check basic format (required fields exists?)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            confirm_password = serializer.validated_data['confirm_password']

            # A. Check if New Password matches Confirm Password
            if new_password != confirm_password:
                return Response(
                    {'error': 'New passwords do not match.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # B. Verify Old Password is correct
            if not user.check_password(old_password):
                return Response(
                    {'error': 'Invalid old password.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # C. Complexity Check (Min 6 chars)
            if len(new_password) < 6:
                return Response(
                    {'error': 'New password must be at least 6 characters long.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # D. Save New Password
            user.set_password(new_password)
            user.save()
            
            return Response(
                {'message': 'Password changed successfully. Please login again.'}, 
                status=status.HTTP_200_OK
            )
            
        # Return errors if fields are missing
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)