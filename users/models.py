from django.contrib.auth.models import AbstractUser
from django.db import models
# from courses.models import School, Class  <-- This line was deleted, it caused an error

# This is the fix. We are moving the Role class outside
# and using the display names as the values.
class Role(models.TextChoices):
    SUPER_ADMIN = 'Super Admin', 'Super Admin'
    SCHOOL_ADMIN = 'School Admin', 'School Admin'
    TEACHER = 'Teacher', 'Teacher'
    STUDENT = 'Student', 'Student'

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    We add a 'role' to distinguish between user types and link
    users to a School and (if a student) a Class.
    """
    
    # Use the new Role class for choices
    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.STUDENT
    )
    
    school = models.ForeignKey(
        'courses.School', # Use string path to avoid circular import
        on_delete=models.CASCADE,
        null=True, 
        blank=True,
        related_name='users'
    )
    
    assigned_class = models.ForeignKey(
        'courses.Class', # Use string path to avoid circular import
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )

    def __str__(self):
        return self.username