from rest_framework import serializers
from .models import School, Class, Subject, Lecture, Attendance

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

        # Corrected to use '__all__' to include only model fields