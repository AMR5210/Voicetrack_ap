from django.contrib import admin
from .models import VoiceRecording, AnalysisResult, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']
    list_filter = ['created_at']


@admin.register(VoiceRecording)
class VoiceRecordingAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'duration', 'file_size', 'created_at']
    search_fields = ['title', 'user__username']
    list_filter = ['created_at', 'user']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'audio_file')
        }),
        ('Metadata', {
            'fields': ('duration', 'file_size', 'metadata')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['recording', 'status', 'processed_at', 'processing_time']
    search_fields = ['recording__title', 'recording__user__username']
    list_filter = ['status', 'processed_at']
    readonly_fields = ['processed_at']
    
    fieldsets = (
        ('Recording', {
            'fields': ('recording', 'status')
        }),
        ('Audio Features', {
            'fields': ('pitch_mean', 'pitch_std', 'intensity_mean', 'intensity_std', 'speech_rate')
        }),
        ('Advanced Analysis', {
            'fields': ('features', 'insights'),
            'classes': ('collapse',)
        }),
        ('Processing Info', {
            'fields': ('processed_at', 'processing_time', 'error_message'),
            'classes': ('collapse',)
        }),
    )
