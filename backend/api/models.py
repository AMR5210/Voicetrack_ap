from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class VoiceRecording(models.Model):
    """Model for storing voice recording metadata"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recordings')
    title = models.CharField(max_length=255)
    audio_file = models.FileField(upload_to='recordings/%Y/%m/%d/')
    duration = models.FloatField(help_text="Duration in seconds", null=True, blank=True)
    file_size = models.IntegerField(help_text="File size in bytes", null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class AnalysisResult(models.Model):
    """Model for storing audio analysis results"""
    recording = models.OneToOneField(
        VoiceRecording, 
        on_delete=models.CASCADE, 
        related_name='analysis'
    )
    
    # Basic audio features
    pitch_mean = models.FloatField(null=True, blank=True, help_text="Mean pitch in Hz")
    pitch_std = models.FloatField(null=True, blank=True, help_text="Pitch standard deviation")
    intensity_mean = models.FloatField(null=True, blank=True, help_text="Mean intensity/volume")
    intensity_std = models.FloatField(null=True, blank=True, help_text="Intensity standard deviation")
    speech_rate = models.FloatField(null=True, blank=True, help_text="Words per minute")
    
    # Advanced features stored as JSON
    features = models.JSONField(default=dict, blank=True, help_text="Additional audio features")
    
    # AI-generated insights
    insights = models.TextField(blank=True, help_text="AI-generated analysis and insights")
    
    # Processing metadata
    processed_at = models.DateTimeField(default=timezone.now)
    processing_time = models.FloatField(null=True, blank=True, help_text="Processing time in seconds")
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-processed_at']

    def __str__(self):
        return f"Analysis for {self.recording.title}"


class UserProfile(models.Model):
    """Extended user profile for additional user information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"
