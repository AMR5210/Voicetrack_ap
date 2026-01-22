from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import time
import os
import tempfile

from .models import VoiceRecording, AnalysisResult, UserProfile
from .serializers import (
    UserSerializer, 
    UserRegistrationSerializer,
    UserProfileSerializer,
    VoiceRecordingSerializer,
    VoiceRecordingCreateSerializer,
    AnalysisResultSerializer
)
from .utils.audio_processor import process_audio_file


# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current authenticated user details"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# User Profile Views
class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profiles"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only access their own profile
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


# Voice Recording Views
class VoiceRecordingViewSet(viewsets.ModelViewSet):
    """ViewSet for voice recordings"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only access their own recordings
        return VoiceRecording.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VoiceRecordingCreateSerializer
        return VoiceRecordingSerializer
    
    def perform_create(self, serializer):
        """Create recording, associate with user, and trigger audio analysis"""
        recording = serializer.save(user=self.request.user)
        
        # Only auto-process in development (librosa has issues on App Engine)
        from django.conf import settings
        if settings.DEBUG:
            # Automatically trigger analysis in development
            self._process_audio_async(recording)
        else:
            # On production, create pending analysis for manual trigger
            AnalysisResult.objects.create(
                recording=recording,
                status='pending'
            )
    
    def create(self, request, *args, **kwargs):
        """Override create to return full serializer with ID"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return the full recording data using the read serializer
        instance = serializer.instance
        output_serializer = VoiceRecordingSerializer(instance, context={'request': request})
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def _process_audio_async(self, recording):
        """Process audio file and create analysis result"""
        # Create analysis record
        analysis = AnalysisResult.objects.create(
            recording=recording,
            status='processing'
        )
        
        try:
            start_time = time.time()
            
            # Get the audio file path
            audio_file_path = recording.audio_file.path if hasattr(recording.audio_file, 'path') else None
            
            if not audio_file_path:
                # Handle case where file is in cloud storage
                # Download temporarily for processing
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    for chunk in recording.audio_file.chunks():
                        tmp_file.write(chunk)
                    audio_file_path = tmp_file.name
                
                temp_file_created = True
            else:
                temp_file_created = False
            
            # Process the audio
            result = process_audio_file(audio_file_path)
            
            # Clean up temp file if created
            if temp_file_created and os.path.exists(audio_file_path):
                os.remove(audio_file_path)
            
            processing_time = time.time() - start_time
            
            if result['status'] == 'success':
                features = result['features']
                
                # Update analysis with results
                analysis.pitch_mean = features.get('pitch_mean')
                analysis.pitch_std = features.get('pitch_std')
                analysis.intensity_mean = features.get('intensity_mean')
                analysis.intensity_std = features.get('intensity_std')
                analysis.speech_rate = features.get('speech_rate')
                analysis.features = features
                analysis.insights = result['insights']
                analysis.status = 'completed'
                analysis.processing_time = processing_time
                
                # Also update recording duration
                recording.duration = features.get('duration', 0)
                recording.save()
            else:
                analysis.status = 'failed'
                analysis.error_message = result.get('error_message', 'Unknown error')
            
            analysis.save()
            
        except Exception as e:
            analysis.status = 'failed'
            analysis.error_message = str(e)
            analysis.save()
    
    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        """Get analysis results for a recording"""
        recording = self.get_object()
        
        try:
            analysis = recording.analysis
            serializer = AnalysisResultSerializer(analysis)
            return Response(serializer.data)
        except AnalysisResult.DoesNotExist:
            return Response(
                {'detail': 'Analysis not yet available for this recording'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def trigger_analysis(self, request, pk=None):
        """Manually trigger analysis for a recording"""
        recording = self.get_object()
        
        # Check if analysis already exists
        try:
            analysis = recording.analysis
            if analysis.status == 'completed':
                return Response(
                    {'detail': 'Analysis already completed', 'analysis_id': analysis.id},
                    status=status.HTTP_200_OK
                )
            # Re-process if failed or pending
            analysis.delete()
        except AnalysisResult.DoesNotExist:
            pass
        
        # Trigger new analysis
        self._process_audio_async(recording)
        
        # Get the newly created analysis
        analysis = recording.analysis
        
        return Response(
            {
                'detail': 'Analysis started',
                'analysis_id': analysis.id,
                'status': analysis.status
            },
            status=status.HTTP_202_ACCEPTED
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user's recording statistics"""
        recordings = self.get_queryset()
        
        stats = {
            'total_recordings': recordings.count(),
            'total_duration': sum([r.duration or 0 for r in recordings]),
            'analyzed_count': recordings.filter(analysis__status='completed').count(),
            'pending_analysis': recordings.filter(analysis__status='pending').count(),
            'failed_analysis': recordings.filter(analysis__status='failed').count(),
        }
        
        return Response(stats)


# Analysis Result Views
class AnalysisResultViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for analysis results (read-only)"""
    serializer_class = AnalysisResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only access analysis for their own recordings
        return AnalysisResult.objects.filter(recording__user=self.request.user)


# Health check endpoint
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """API health check endpoint"""
    return Response({
        'status': 'healthy',
        'message': 'VoiceTrack API is running'
    })
