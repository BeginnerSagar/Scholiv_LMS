from django.db import models
from django.conf import settings

# Get the User model we defined in our 'users' app
User = settings.AUTH_USER_MODEL

class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Class(models.Model):
    # e.g., "Class 10", "Class 12"
    name = models.CharField(max_length=100) 
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')

    def __str__(self):
        return f"{self.name} - {self.school.name}"

    class Meta:
        verbose_name_plural = "Classes"

class Subject(models.Model):
    name = models.CharField(max_length=100) # e.g., "Mathematics"
    
    def __str__(self):
        return self.name

class Lecture(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField(max_length=1024, blank=True, null=True)
    # You can also use FileField for local uploads:
    # video_file = models.FileField(upload_to='lectures/', blank=True, null=True)
    
    # Relationships based on requirements
    class_assigned = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, related_name='lectures')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, related_name='lectures')
    topic = models.CharField(max_length=255, blank=True, null=True) # e.g., "Chapter 1: Algebra"
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    lecture = models.ForeignKey(Lecture, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    present = models.BooleanField(default=False)
    
    # This will be used for the "auto-mark present" feature
    watched_video = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.student.username} - {self.date} - Present: {self.present}"

