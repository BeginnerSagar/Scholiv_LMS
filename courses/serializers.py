from rest_framework import serializers
from .models import (
    School, 
    Class, 
    Subject, 
    Lecture, 
    Attendance,
    Announcement,
    Question,
    Answer
)

# --- Core CRUD Serializers ---

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'address']


class ClassSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = Class
        fields = ['id', 'name', 'school', 'school_name']
        extra_kwargs = {
            'school': {'write_only': True}
        }


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']


class LectureSerializer(serializers.ModelSerializer):
    class_assigned_name = serializers.CharField(source='class_assigned.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = Lecture
        fields = [
            'id', 'title', 'description', 
            'video_url', 'video_file',
            'class_assigned', 'class_assigned_name', 
            'subject', 'subject_name',
            'topic',
            'uploaded_at'
        ]
        extra_kwargs = {
            'class_assigned': {'write_only': True},
            'subject': {'write_only': True},
        }
        read_only_fields = ['uploaded_at']


class AttendanceSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source='student.username', read_only=True)
    lecture_title = serializers.CharField(source='lecture.title', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'student_username',
            'lecture', 'lecture_title',
            'date', 'present', 'watched_video'
        ]
        extra_kwargs = {
            'student': {'write_only': True},
            'lecture': {'write_only': True},
        }


class AttendanceUploadSerializer(serializers.Serializer):
    """
    Serializer for attendance Excel file upload.
    """
    file = serializers.FileField()


# --- Q&A and Announcement Serializers ---

class AnnouncementSerializer(serializers.ModelSerializer):
    """
    Serializer for Announcements.
    Matches your actual model structure with title, priority, etc.
    """
    posted_by_username = serializers.CharField(source='posted_by.username', read_only=True)
    target_class_name = serializers.CharField(source='target_class.name', read_only=True)
    school_name = serializers.CharField(source='target_class.school.name', read_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 
            'title',
            'content',
            'posted_by',
            'posted_by_username',
            'target_class',
            'target_class_name',
            'school_name',
            'priority',
            'created_at',
            'updated_at'
        ]
        extra_kwargs = {
            'posted_by': {'write_only': True},
            'target_class': {'write_only': True},
        }
        read_only_fields = ['posted_by_username', 'target_class_name', 'school_name', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """
        Automatically set the posted_by field to the current user.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['posted_by'] = request.user
        return super().create(validated_data)


class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer for Answers.
    Matches your model with is_accepted, updated_at, etc.
    """
    answered_by_username = serializers.CharField(source='answered_by.username', read_only=True)
    
    class Meta:
        model = Answer
        fields = [
            'id',
            'content',
            'question',
            'answered_by',
            'answered_by_username',
            'is_accepted',
            'created_at',
            'updated_at'
        ]
        extra_kwargs = {
            'question': {'write_only': True},
            'answered_by': {'write_only': True},
        }
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        """
        Automatically set the answered_by field to the current user.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['answered_by'] = request.user
        return super().create(validated_data)


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for Questions.
    Matches your model with is_answered, updated_at, and nested answers.
    """
    asked_by_username = serializers.CharField(source='asked_by.username', read_only=True)
    lecture_title = serializers.CharField(source='lecture.title', read_only=True)
    
    # Nested answers - shows all answers for this question
    answers = AnswerSerializer(many=True, read_only=True)
    answer_count = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 
            'title',
            'content',
            'asked_by',
            'asked_by_username',
            'lecture',
            'lecture_title',
            'is_answered',
            'answers',
            'answer_count',
            'created_at',
            'updated_at'
        ]
        extra_kwargs = {
            'asked_by': {'write_only': True},
            'lecture': {'write_only': True},
        }
        read_only_fields = ['is_answered', 'created_at', 'updated_at']
    
    def get_answer_count(self, obj):
        """
        Return the number of answers for this question.
        """
        return obj.answers.count()
    
    def create(self, validated_data):
        """
        Automatically set the asked_by field to the current user.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['asked_by'] = request.user
        return super().create(validated_data)
    
    
class AttendanceUploadSerializer(serializers.Serializer):
    """    Serializer for attendance Excel file upload."""
    file = serializers.FileField()
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(required=True, style={'input_type': 'password'})