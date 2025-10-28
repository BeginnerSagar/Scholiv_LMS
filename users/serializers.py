from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Make sure to import the User model from its new location
from .models import User 


class UserSerializer(serializers.ModelSerializer):
    """
    A read-only serializer to safely display user data.
    We explicitly list the fields to ensure the password is NEVER exposed.
    """
    # We add 'school_name' and 'class_name' for easier display on the frontend
    school_name = serializers.CharField(source='school.name', read_only=True)
    class_name = serializers.CharField(source='assigned_class.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'school', 'school_name', 'assigned_class', 'class_name']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    A write-only serializer for handling new user registration.
    NOTE: This is for single user sign-up (like our old one). We will
    use a different serializer for the bulk upload.
    """
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password] # Use Django's built-in password validation
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')

    def validate(self, attrs):
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "This email address is already in use."})
        
        # Check if username already exists
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})
            
        return attrs

    def create(self, validated_data):
        # Use .create_user() to ensure the password is properly hashed
        # Default to 'student'
        user = User.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'student') 
        )
        return user

# --- THIS IS THE NEW CLASS FOR STEP 6.3 ---

class StudentUploadSerializer(serializers.Serializer):
    """
    This serializer is not a ModelSerializer. It's a plain Serializer
    used only to validate that a file has been uploaded.
    """
    file = serializers.FileField()

    class Meta:
        fields = ('file',)

