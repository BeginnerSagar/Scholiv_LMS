from django.db import models
from django.conf import settings

# Note: We use settings.AUTH_USER_MODEL to refer to our custom User model.
# This is Django's recommended best practice.

class Course(models.Model):
    """
    Represents a course created by an instructor.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="A detailed description of the course.")
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_taught',
        limit_choices_to={'role': 'instructor'} # Ensures only instructors can be assigned
    )
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    thumbnail_url = models.URLField(blank=True, null=True, help_text="A URL to the course's thumbnail image.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Module(models.Model):
    """
    A module is a section or chapter within a course.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0, help_text="The order of the module within the course.")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    """
    A lesson is a single learning unit within a module, e.g., a video or an article.
    """
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, help_text="Text content for the lesson.")
    video_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="The order of the lesson within the module.")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    """
    Connects a student (User) to a Course, representing their enrollment.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'} # Ensures only students can enroll
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolled_students')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures a student can only enroll in the same course once.
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

