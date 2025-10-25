from rest_framework import serializers
from .models import School, Class, Subject, Lecture, Attendance

class SchoolSerializer(serializers.ModelSerializer):
    """
    Serializer for the School model.
    """
    class Meta:
        model = School
        fields = ['id', 'name', 'address']

class ClassSerializer(serializers.ModelSerializer):
    """
    Serializer for the Class model.
    """
    class Meta:
        model = Class
        fields = ['id', 'name', 'school']

class SubjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Subject model.
    """
    class Meta:
        model = Subject
        fields = ['id', 'name']

class LectureSerializer(serializers.ModelSerializer):
    """
    Serializer for the Lecture model.
    """
    class Meta:
        model = Lecture
        fields = ['id', 'title', 'description', 'video_url', 'topic', 'class_assigned', 'subject']

class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Attendance model.
    """
    class Meta:
        model = Attendance
        fields = ['id', 'student', 'lecture', 'date', 'is_present']

