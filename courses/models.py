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
    
    # OPTION 1: Store video URL (for external videos like YouTube, Vimeo)
    video_url = models.URLField(max_length=1024, blank=True, null=True, 
                                 help_text="External video URL (YouTube, Vimeo, etc.)")
    
    # OPTION 2: Upload video file to S3
    video_file = models.FileField(
        upload_to='lectures/videos/',  # Files will be stored in S3: bucket/lectures/videos/
        blank=True, 
        null=True,
        help_text="Upload video file (will be stored on AWS S3)"
    )
    
    # Video metadata
    duration_minutes = models.IntegerField(blank=True, null=True, help_text="Video duration in minutes")
    file_size_mb = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, 
                                       help_text="File size in MB")
    
    # Relationships based on requirements
    class_assigned = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, related_name='lectures')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, related_name='lectures')
    topic = models.CharField(max_length=255, blank=True, null=True) # e.g., "Chapter 1: Algebra"
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_video_url(self):
        """
        Returns the appropriate video URL:
        - If video_file exists, return S3 URL
        - Otherwise return external video_url
        """
        if self.video_file:
            return self.video_file.url
        return self.video_url

class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    lecture = models.ForeignKey(Lecture, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    present = models.BooleanField(default=False)
    
    # This will be used for the "auto-mark present" feature
    watched_video = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.student.username} - {self.date} - Present: {self.present}"


# ===========================
# Q&A SYSTEM MODELS
# ===========================

class Announcement(models.Model):
    title = models.CharField(max_length=255, default="Untitled")
    content = models.TextField(blank=True, null=True)

    
    # Who posted this announcement
    posted_by = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='announcements_posted',
    default=1
)

    
    # Which class should see this announcement
    target_class = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE, 
        related_name='announcements'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Priority level (optional feature for later)
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='medium'
    )

    class Meta:
        ordering = ['-created_at']  # Show newest first

    def __str__(self):
        return f"{self.title} - {self.target_class.name}"


class Question(models.Model):
    """
    Questions that Students can ask about a specific lecture.
    """
    title = models.CharField(max_length=255, default="Untitled")
    content = models.TextField()

    
    # Who asked this question
    asked_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='questions_asked'
    )
    
    # Which lecture is this question about
    lecture = models.ForeignKey(
        Lecture, 
        on_delete=models.CASCADE, 
        related_name='questions'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Track if the question has been answered
    is_answered = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']  # Show newest first

    def __str__(self):
        return f"Q: {self.title} by {self.asked_by.username}"


class Answer(models.Model):
    """
    Answers that Teachers can provide to student questions.
    """
    content = models.TextField()
    
    # Which question is this answering
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='answers'
    )
    
    # Who answered this question
    answered_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='answers_given'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Mark if this is the "accepted" or "best" answer
    is_accepted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']  # Show oldest first (chronological)

    def __str__(self):
        return f"A: {self.content[:50]}... by {self.answered_by.username}"

    def save(self, *args, **kwargs):
        """
        Override save to automatically mark the question as answered.
        """
        super().save(*args, **kwargs)
        # When an answer is saved, mark the question as answered
        self.question.is_answered = True
        self.question.save()