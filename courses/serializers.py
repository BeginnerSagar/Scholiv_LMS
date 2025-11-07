from rest_framework import serializers
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
from users.models import User

# --- Admin Portal: Core CRUD Serializers (Phase 4) ---

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'address', 'created_at']

class ClassSerializer(serializers.ModelSerializer):
    # Use 'school_name' for reading, 'school_id' for writing
    school_name = serializers.StringRelatedField(source='school', read_only=True)
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(), source='school', write_only=True
    )

    class Meta:
        model = Class
        fields = ['id', 'name', 'school_name', 'school_id', 'created_at']


class SubjectSerializer(serializers.ModelSerializer):
    # Use 'school_name' for reading, 'school_id' for writing
    school_name = serializers.StringRelatedField(source='school', read_only=True)
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(), source='school', write_only=True
    )
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'school_name', 'school_id', 'created_at']

class LectureSerializer(serializers.ModelSerializer):
    # Add readable names for foreign keys
    class_assigned_name = serializers.StringRelatedField(source='class_assigned', read_only=True)
    subject_name = serializers.StringRelatedField(source='subject', read_only=True)
    
    class Meta:
        model = Lecture
        fields = [
            'id', 'title', 'description', 
            'video_url', 'video_file', 
            'class_assigned', 'class_assigned_name', 
            'subject', 'subject_name', 'uploaded_at'
        ]
        # Make the ID fields write-only
        extra_kwargs = {
            'class_assigned': {'write_only': True},
            'subject': {'write_only': True},
        }


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__' # This will include student, lecture, date, and is_present


# --- Admin Portal: Advanced Features (Phase 5) ---

class AttendanceUploadSerializer(serializers.Serializer):
    """
    Serializer for the Teacher's attendance Excel file upload.
    This serializer only validates that a file was uploaded.
    """
    file = serializers.FileField()


# --- NEW: Q&A and Announcement Serializers (Step 6.19) - CORRECTED ---

class AnnouncementSerializer(serializers.ModelSerializer):
    """
    Serializer for Announcements.
    We show readable names for foreign keys.
    """
    # Renamed 'teacher' to 'teacher_name' to avoid conflict
    teacher_name = serializers.StringRelatedField(source='teacher', read_only=True)
    # Renamed 'school' to 'school_name' to avoid conflict
    school_name = serializers.StringRelatedField(source='school', read_only=True)
    
    # Use 'class_assigned_name' for reading, 'class_assigned_id' for writing
    class_assigned_name = serializers.StringRelatedField(source='class_assigned', read_only=True)
    class_assigned_id = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(), source='class_assigned', write_only=True
    )

    class Meta:
        model = Announcement
        # Updated fields list with new names
        fields = [
            'id', 'teacher_name', 'school_name', 
            'class_assigned_id', 'class_assigned_name', 
            'content', 'created_at'
        ]


class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer for Answers.
    Shows the teacher's username.
    """
    # Renamed 'teacher' to 'teacher_name' to avoid conflict
    teacher_name = serializers.StringRelatedField(source='teacher', read_only=True)
    
    class Meta:
        model = Answer
        # Updated fields list
        fields = ['id', 'teacher_name', 'question', 'content', 'created_at']


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for Questions.
    Shows the student's username and includes all related answers.
    """
    # Renamed 'student' to 'student_name' to avoid conflict
    student_name = serializers.StringRelatedField(source='student', read_only=True)
    
    # Use 'lecture_name' for reading, 'lecture_id' for writing
    lecture_name = serializers.StringRelatedField(source='lecture', read_only=True)
    lecture_id = serializers.PrimaryKeyRelatedField(
        queryset=Lecture.objects.all(), source='lecture', write_only=True
    )
    
    # This automatically includes all answers related to this question
    answers = AnswerSerializer(many=True, read_only=True) 

    class Meta:
        model = Question
        # Updated fields list
        fields = [
            'id', 'student_name', 
            'lecture_id', 'lecture_name', 
            'title', 'content', 'created_at', 'answers'
        ]