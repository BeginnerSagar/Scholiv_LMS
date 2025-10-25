from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    We add a 'role' to distinguish between students and admins.
    This is the central model for all users in the application.
    """
    
    # --- CHANGE 1: Updated Roles ---
    # Based on the requirement doc, we only have 'student' and 'admin'
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'), 
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    # --- CHANGE 2: Link Student to a Class ---
    # This links a student user to their assigned class.
    # We use 'courses.Class' as a string because the Class model is in another app.
    assigned_class = models.ForeignKey(
        'courses.Class',
        on_delete=models.SET_NULL, # If a class is deleted, the student isn't deleted
        null=True,                # Allows this field to be empty in the database
        blank=True,               # Allows this field to be empty in forms (like the admin panel)
        related_name='students'   # Lets us easily get all students in a class, e.g., my_class.students.all()
    )
    # ------------------------------------

    def __str__(self):
        return self.username

