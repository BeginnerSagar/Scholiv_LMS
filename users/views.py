from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer


class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration.
    Allows any user (authenticated or not) to create a new user account.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        """
        Overrides the default create method to return a custom success message
        and user data using the read-only UserSerializer.
        """
        serializer = self.get_serializer(data=request.data)
        # is_valid will automatically run our custom validate_email method
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # We use the UserSerializer to format the response data, ensuring
        # the password is not included in the success response.
        user_data = UserSerializer(user, context=self.get_serializer_context()).data

        return Response({
            "user": user_data,
            "message": "User registered successfully."
        }, status=status.HTTP_201_CREATED)

