from django.contrib.auth.models import AbstractUser
from django.db import models

# Import the 'School' and 'Class' models from the 'courses' app
# We use 'import courses.models' to avoid circular import issues
import courses.models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    We add a 'role' to distinguish between user types and link
    users to a specific school and class.
    """

    # Define the new 4-role system
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('school_admin', 'School Admin'),
        ('super_admin', 'Super Admin'), # This is for YOU (Scholive staff)
    )
    
    # We keep 'student' as the default for new registrations
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='student'
    )

    # This is the NEW, most important field.
    # It links every user to a specific school.
    # SuperAdmins might not belong to a school, so we allow it to be blank.
    school = models.ForeignKey(
        'courses.School',  # Links to the School model in the 'courses' app
        on_delete=models.SET_NULL,  # If a school is deleted, keep the user account
        null=True,  # Allows SuperAdmins to not have a school
        blank=True,
        related_name='staff_and_students' # e.g., my_school.staff_and_students.all()
    )

    # We keep this field to link students to their specific class
    assigned_class = models.ForeignKey(
        'courses.Class',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students' # e.g., my_class.students.all()
    )

    def __str__(self):
        return self.username

