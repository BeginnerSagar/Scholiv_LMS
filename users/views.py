from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated 
from rest_framework.views import APIView # Needed for the custom upload view
import openpyxl # For reading Excel files
import secrets # For generating random passwords
import string

# Import the User model from its new location
from .models import User 
# Import the relevant course models
from courses.models import Class 
# Import the new serializers
from .serializers import UserRegistrationSerializer, UserSerializer, StudentUploadSerializer 
# Import our custom permissions
from courses.permissions import IsSchoolAdmin

# --- Existing User Registration View ---
class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration.
    Allows any user (authenticated or not) to create a new user account.
    Defaults new users to the 'student' role.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,) # Anyone can register

    def perform_create(self, serializer):
        # We override perform_create to potentially customize role if needed,
        # but the serializer's create method handles hashing and defaults the role.
        user = serializer.save()
        # Optionally, you could add logic here, e.g., send a welcome email.

    def create(self, request, *args, **kwargs):
        """
        Overrides the default create method to return a custom success message
        and user data using the read-only UserSerializer.
        """
        serializer = self.get_serializer(data=request.data)
        # is_valid will automatically run our custom validate_email method
        serializer.is_valid(raise_exception=True) 
        user = self.perform_create(serializer) # Changed this line
        
        # We use the UserSerializer to format the response data, ensuring
        # the password is not included in the success response.
        user_data = UserSerializer(user, context=self.get_serializer_context()).data

        return Response({
            "user": user_data,
            "message": "User registered successfully."
        }, status=status.HTTP_201_CREATED)


# --- NEW STUDENT UPLOAD VIEW FOR STEP 6.4 ---

class StudentUploadView(APIView):
    """
    API View for School Admins to bulk upload students via an Excel file.
    """
    serializer_class = StudentUploadSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdmin] # Only School Admins

    def generate_random_password(self, length=12):
        """Generates a secure random password."""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        return password

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data['file']
        school_admin = request.user # The logged-in School Admin

        if not school_admin.school:
             return Response(
                {"error": "Admin user is not associated with any school."},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_count = 0
        errors = []

        try:
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active

            # Iterate over rows, starting from the second row to skip the header
            for row_idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
                # Ensure all cells exist, use None if empty
                username = row[0].value if len(row) > 0 and row[0].value else None
                email = row[1].value if len(row) > 1 and row[1].value else None
                password = row[2].value if len(row) > 2 and row[2].value else None
                class_name = row[3].value if len(row) > 3 and row[3].value else None

                # --- Basic Data Validation ---
                if not username or not email or not class_name:
                    errors.append(f"Row {row_idx}: Missing required data (Username, Email, Class Name).")
                    continue

                # --- Find the Class ---
                try:
                    assigned_class = Class.objects.get(name=class_name, school=school_admin.school)
                except Class.DoesNotExist:
                    errors.append(f"Row {row_idx}: Class '{class_name}' not found for this school.")
                    continue
                except Class.MultipleObjectsReturned:
                     errors.append(f"Row {row_idx}: Multiple classes found with name '{class_name}'. Please ensure class names are unique within the school.")
                     continue


                # --- Check if user already exists (by email or username) ---
                if User.objects.filter(email=email).exists():
                    errors.append(f"Row {row_idx}: Email '{email}' already exists.")
                    continue
                if User.objects.filter(username=username).exists():
                    errors.append(f"Row {row_idx}: Username '{username}' already exists.")
                    continue

                # --- Determine Password ---
                if not password:
                    password = self.generate_random_password()
                    # You might want to log this generated password or email it,
                    # but for now, we just create the user.

                # --- Create the User ---
                try:
                    User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        role='student', # Explicitly set role
                        school=school_admin.school, # Assign to admin's school
                        assigned_class=assigned_class # Assign to the found class
                    )
                    created_count += 1
                except Exception as e: # Catch any other potential errors during user creation
                     errors.append(f"Row {row_idx}: Failed to create user '{username}'. Error: {str(e)}")


        except Exception as e:
            return Response(
                {"error": f"Failed to process the Excel file. Please ensure it's a valid .xlsx file and follows the template. Error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Return Summary ---
        response_status = status.HTTP_201_CREATED if created_count > 0 and not errors else status.HTTP_400_BAD_REQUEST
        return Response({
            "message": f"Processed Excel file. Created {created_count} new student(s).",
            "errors": errors
        }, status=response_status)

