from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """
    Profile extension linking to Django's default User to distinguish 
    between Student and Company accounts.
    """
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('company', 'Company'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    company_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"


class Job(models.Model):
    """
    Job postings created by Company users.
    """
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.JSONField(default=list)  # list of skill keywords
    min_score = models.IntegerField(default=70)       # minimum required match score (0-100)
    experience_required = models.CharField(max_length=100) # e.g. "Entry Level", "1-3 Years"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        company_name = self.company.profile.company_name or self.company.username
        return f"{self.title} at {company_name}"


class ResumeAnalysis(models.Model):
    """
    Stores PDF extraction metrics, detected skills, ATS score, and feedback suggestions.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    resume_file = models.FileField(upload_to='resumes/')
    filename = models.CharField(max_length=255)
    extracted_text = models.TextField()
    skills_found = models.JSONField(default=list)
    ats_score = models.IntegerField(default=0)
    suggestions = models.JSONField(default=list)
    recommended_roles = models.JSONField(default=list)
    recommended_companies = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Resume Analyses'

    def __str__(self):
        return f"{self.user.username} - {self.filename} ({self.ats_score}%)"


class Application(models.Model):
    """
    Records job applications submitted by students, tracking match percentage and status.
    """
    STATUS_CHOICES = (
        ('Highly Recommended', 'Highly Recommended'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    match_score = models.IntegerField(default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Rejected')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('student', 'job')  # Prevent applying to the same job multiple times

    def __str__(self):
        return f"{self.student.username} applied to {self.job.title} ({self.match_score}%)"


# Signal receivers to automatically generate Profile rows on user creation
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    instance.profile.save()
