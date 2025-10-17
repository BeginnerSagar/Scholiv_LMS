from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying User model data.
    This is a read-only serializer used to safely show user information.
    """

    class Meta:
        model = User
        # Fields to include in the API output.
        # We explicitly exclude sensitive information like the password hash.
        fields = ['id', 'username', 'email', 'role']

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for handling new user registration.
    It validates input and properly handles password hashing.
    """
    # Define password as a write-only field. This means it can be used for
    # creating/updating an object, but will never be included in the API response.
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'} # Helps DRF's browsable API render a password input.
    )

    class Meta:
        model = User
        # These are the fields the frontend will send when a new user registers.
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {
            'role': {'required': False} # Makes the role optional during registration.
        }

    def validate_email(self, value):
        """
        Check that the email is unique in the database.
        """
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        """
        This method is called when `.save()` is run on the serializer instance.
        It overrides the default create method to use Django's `create_user`
        helper function, which correctly handles password hashing.
        """
        # Set a default role of 'student' if one isn't provided.
        role = validated_data.get('role', 'student')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=role
        )
        return user

