from rest_framework import serializers
from django.contrib.auth.models import User
from .models import VoiceRecording, AnalysisResult, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        # Create user profile automatically
        UserProfile.objects.create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'bio', 'date_of_birth', 'phone_number', 'avatar', 'created_at']
        read_only_fields = ['id', 'created_at']


class AnalysisResultSerializer(serializers.ModelSerializer):
    """Serializer for AnalysisResult model"""
    class Meta:
        model = AnalysisResult
        fields = [
            'id', 'pitch_mean', 'pitch_std', 'intensity_mean', 
            'intensity_std', 'speech_rate', 'features', 'insights',
            'processed_at', 'processing_time', 'status', 'error_message'
        ]
        read_only_fields = ['id', 'processed_at']


class VoiceRecordingSerializer(serializers.ModelSerializer):
    """Serializer for VoiceRecording model"""
    user = UserSerializer(read_only=True)
    analysis = AnalysisResultSerializer(read_only=True)
    audio_file_url = serializers.SerializerMethodField()

    class Meta:
        model = VoiceRecording
        fields = [
            'id', 'user', 'title', 'audio_file', 'audio_file_url',
            'duration', 'file_size', 'metadata', 'analysis',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_audio_file_url(self, obj):
        """Get the full URL for the audio file"""
        if obj.audio_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.audio_file.url)
            return obj.audio_file.url
        return None


class VoiceRecordingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating voice recordings"""
    class Meta:
        model = VoiceRecording
        fields = ['title', 'audio_file', 'metadata']

    def validate_audio_file(self, value):
        """Validate audio file type and size"""
        # Check file extension
        valid_extensions = ['.wav', '.mp3', '.m4a', '.ogg', '.flac']
        ext = value.name.lower()[value.name.rfind('.'):]
        if ext not in valid_extensions:
            raise serializers.ValidationError(
                f"Unsupported file format. Allowed formats: {', '.join(valid_extensions)}"
            )
        
        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size too large. Maximum size is 50MB"
            )
        
        return value

    def create(self, validated_data):
        """Create recording with file size"""
        audio_file = validated_data.get('audio_file')
        if audio_file:
            validated_data['file_size'] = audio_file.size
        return super().create(validated_data)
