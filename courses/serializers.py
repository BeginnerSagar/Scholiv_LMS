from rest_framework import serializers
from .models import School, Class, Subject, Lecture, Attendance, Announcement, Question, Answer
from django.contrib.auth import get_user_model

User = get_user_model()

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    """
    This is the corrected serializer.
    By using 'fields = "__all__"', it will now correctly only use the
    fields that exist on the Attendance model:
    'id', 'student', 'lecture', and 'date'.
    """
    class Meta:
        model = Attendance
        fields = '__all__'


# ===========================
# NEW SERIALIZERS FOR Q&A SYSTEM
# ===========================

class AnnouncementSerializer(serializers.ModelSerializer):
    """
    Serializer for Announcements.
    Includes extra fields to show who posted it and the target class name.
    """
    posted_by_username = serializers.CharField(source='posted_by.username', read_only=True)
    target_class_name = serializers.CharField(source='target_class.name', read_only=True)
    
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
            'priority',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['posted_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """
        Automatically set the posted_by field to the current user.
        """
        # Get the current user from the context
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['posted_by'] = request.user
        return super().create(validated_data)


class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer for Answers.
    Shows who answered and when.
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
        read_only_fields = ['answered_by', 'created_at', 'updated_at']
    
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
    Includes nested answers and extra info about who asked.
    """
    asked_by_username = serializers.CharField(source='asked_by.username', read_only=True)
    lecture_title = serializers.CharField(source='lecture.title', read_only=True)
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
        read_only_fields = ['asked_by', 'is_answered', 'created_at', 'updated_at']
    
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