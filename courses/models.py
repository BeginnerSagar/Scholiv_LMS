from django.db import models
from users.models import User

class School(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Class(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.name} - {self.school.name}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='subjects')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.school.name}"


class Lecture(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Video URL for external links (YouTube, Vimeo, etc.)
    video_url = models.URLField(max_length=1024, blank=True, null=True)
    
    # UPDATED: Uncommented FileField for S3 upload
    # This will automatically upload to AWS S3 when a file is provided
    video_file = models.FileField(
        upload_to='lectures/',  # S3 folder structure
        blank=True, 
        null=True,
        help_text="Upload video file (will be stored in AWS S3)"
    )
    
    # Relationships based on requirements
    class_assigned = models.ForeignKey(
        Class, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='lectures'
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='lectures'
    )
    topic = models.CharField(max_length=255, blank=True, null=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.subject.name}"

    class Meta:
        ordering = ['-uploaded_at']


class Attendance(models.Model):
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='attendances',
        limit_choices_to={'role': 'STUDENT'}
    )
    lecture = models.ForeignKey(
        Lecture, 
        on_delete=models.CASCADE, 
        related_name='attendances'
    )
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'lecture', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.username} - {self.lecture.title} - {self.date}"


class Announcement(models.Model):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='announcements',
        limit_choices_to={'role': 'TEACHER'}
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='announcements'
    )
    class_assigned = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='announcements'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Announcement by {self.teacher.username} for {self.class_assigned.name}"


class Question(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='questions',
        limit_choices_to={'role': 'STUDENT'}
    )
    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.student.username}"


class Answer(models.Model):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='answers',
        limit_choices_to={'role': 'TEACHER'}
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Answer by {self.teacher.username} to '{self.question.title}'"