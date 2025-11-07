from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
import datetime # Import the datetime module
from django.utils import timezone # --- ADD THIS IMPORT ---

# Import the new, top-level Role class from users.models
from users.models import Role 

# Get the custom User model
User = get_user_model()

# --- Core School & Class Structure ---

class School(models.Model):
    """
    Represents an individual school, like 'Delhi Public School'.
    This is the top-level object for isolating data.
    """
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True, null=True)
    # --- THIS IS THE FIX ---
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.name

class Class(models.Model):
    """
    Represents a specific class within a school, e.g., 'Class 10-A'.
    Linked to one School.
    """
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    # --- THIS IS THE FIX ---
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        verbose_name_plural = "Classes"
        # Ensures a class name is unique within its school
        unique_together = ('name', 'school') 

    def __str__(self):
        return f"{self.name} ({self.school.name})"

class Subject(models.Model):
    """
    Represents a subject, e.g., 'Mathematics', 'Physics'.
    Linked to a School so each school can manage its own subjects.
    """
    name = models.CharField(max_length=100)
    # --- THIS IS THE FIX ---
    # We must add null=True to this new field, otherwise Django
    # will ask for a default for any existing subjects.
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='subjects', null=True)
    # --- THIS IS THE FIX ---
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        # Ensures a subject name is unique within its school
        unique_together = ('name', 'school')

    def __str__(self):
        try:
            return f"{self.name} ({self.school.name})"
        except:
             return self.name

# --- Content Models ---

class Lecture(models.Model):
    """
    Represents a single recorded lecture (the core Scholive content).
    Uploaded by SuperAdmin and linked to a Class and Subject.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    # This 'video_url' is just a placeholder text field for now.
    # We will change this to a FileField in Step 6.14.
    video_url = models.CharField(max_length=1024, blank=True, null=True)
    # This field is for the uploaded video file
    video_file = models.FileField(upload_to='lectures/', null=True, blank=True)
    
    class_assigned = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, related_name='lectures')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, related_name='lectures')
    # --- THIS IS THE FIX ---
    uploaded_at = models.DateTimeField(default=timezone.now, editable=False)
    
    def __str__(self):
        try:
            return f"{self.title} ({self.class_assigned.name})"
        except:
             return self.title

class Attendance(models.Model):
    """
    Links a Student to a Lecture they have attended/watched.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField(default=datetime.date.today) # Added default
    is_present = models.BooleanField(default=True)

    class Meta:
        # A student can only be marked present for a lecture once per day
        unique_together = ('student', 'lecture', 'date')

    def __str__(self):
        return f"{self.student.username} - {self.lecture.title} on {self.date}"

# --- NEW: Q&A and Announcement Models ---

class Announcement(models.Model):
    """
    An announcement posted by a Teacher to their assigned classes.
    """
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements', limit_choices_to={'role': Role.TEACHER})
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='announcements')
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='announcements')
    content = models.TextField()
    # --- THIS IS THE FIX ---
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"Announcement for {self.class_assigned.name} by {self.teacher.username}"

    def save(self, *args, **kwargs):
        # Automatically assign the teacher's school on save
        if not self.school_id:
            self.school = self.teacher.school
        super().save(*args, **kwargs)

class Question(models.Model):
    """
    A question asked by a Student about a specific Lecture.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions', limit_choices_to={'role': Role.STUDENT})
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255)
    content = models.TextField()
    # --- THIS IS THE FIX ---
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"Q: {self.title} (by {self.student.username} on {self.lecture.title})"

class Answer(models.Model):
    """
    An answer posted by a Teacher to a Student's Question.
    """
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers', limit_choices_to={'role': Role.TEACHER})
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    # --- THIS IS THE FIX ---
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"A: by {self.teacher.username} for Q: {self.question.id}"