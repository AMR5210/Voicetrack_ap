"""
Audio processing utilities using librosa
Extracts features from audio files for voice analysis
"""

import librosa
import numpy as np
import soundfile as sf
from typing import Dict, Optional
import os
import tempfile


class AudioProcessor:
    """Process audio files and extract acoustic features"""
    
    def __init__(self, sample_rate: int = 22050):
        """
        Initialize audio processor
        
        Args:
            sample_rate: Target sample rate for audio processing
        """
        self.sample_rate = sample_rate
    
    def load_audio(self, file_path: str) -> tuple:
        """
        Load audio file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            audio_data, sr = librosa.load(file_path, sr=self.sample_rate)
            return audio_data, sr
        except Exception as e:
            raise ValueError(f"Error loading audio file: {str(e)}")
    
    def get_duration(self, audio_data: np.ndarray, sr: int) -> float:
        """
        Get audio duration in seconds
        
        Args:
            audio_data: Audio time series
            sr: Sample rate
            
        Returns:
            Duration in seconds
        """
        return float(librosa.get_duration(y=audio_data, sr=sr))
    
    def extract_pitch_features(self, audio_data: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Extract pitch-related features
        
        Args:
            audio_data: Audio time series
            sr: Sample rate
            
        Returns:
            Dictionary with pitch statistics
        """
        # Extract pitch using piptrack
        pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sr)
        
        # Get pitch values (filter out zeros)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:  # Filter silence
                pitch_values.append(pitch)
        
        if len(pitch_values) > 0:
            pitch_array = np.array(pitch_values)
            return {
                'pitch_mean': float(np.mean(pitch_array)),
                'pitch_std': float(np.std(pitch_array)),
                'pitch_min': float(np.min(pitch_array)),
                'pitch_max': float(np.max(pitch_array)),
                'pitch_median': float(np.median(pitch_array))
            }
        else:
            return {
                'pitch_mean': 0.0,
                'pitch_std': 0.0,
                'pitch_min': 0.0,
                'pitch_max': 0.0,
                'pitch_median': 0.0
            }
    
    def extract_intensity_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """
        Extract intensity/energy features
        
        Args:
            audio_data: Audio time series
            
        Returns:
            Dictionary with intensity statistics
        """
        # Calculate RMS energy
        rms = librosa.feature.rms(y=audio_data)[0]
        
        return {
            'intensity_mean': float(np.mean(rms)),
            'intensity_std': float(np.std(rms)),
            'intensity_min': float(np.min(rms)),
            'intensity_max': float(np.max(rms))
        }
    
    def extract_spectral_features(self, audio_data: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Extract spectral features
        
        Args:
            audio_data: Audio time series
            sr: Sample rate
            
        Returns:
            Dictionary with spectral features
        """
        # Spectral centroid
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)[0]
        
        # Spectral rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)[0]
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
        
        return {
            'spectral_centroid_mean': float(np.mean(spectral_centroids)),
            'spectral_centroid_std': float(np.std(spectral_centroids)),
            'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
            'spectral_rolloff_std': float(np.std(spectral_rolloff)),
            'zero_crossing_rate_mean': float(np.mean(zcr)),
            'zero_crossing_rate_std': float(np.std(zcr))
        }
    
    def estimate_speech_rate(self, audio_data: np.ndarray, sr: int) -> float:
        """
        Estimate speech rate (simplified)
        
        Args:
            audio_data: Audio time series
            sr: Sample rate
            
        Returns:
            Estimated speech rate in syllables per second
        """
        # Detect onsets (simplistic speech rate estimation)
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
        
        duration = self.get_duration(audio_data, sr)
        if duration > 0:
            # Approximate syllables per second
            speech_rate = len(onsets) / duration
            return float(speech_rate)
        return 0.0
    
    def analyze_audio(self, file_path: str) -> Dict:
        """
        Perform complete audio analysis
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with all extracted features
        """
        try:
            # Load audio
            audio_data, sr = self.load_audio(file_path)
            
            # Get duration
            duration = self.get_duration(audio_data, sr)
            
            # Extract features
            pitch_features = self.extract_pitch_features(audio_data, sr)
            intensity_features = self.extract_intensity_features(audio_data)
            spectral_features = self.extract_spectral_features(audio_data, sr)
            speech_rate = self.estimate_speech_rate(audio_data, sr)
            
            # Combine all features
            analysis_results = {
                'duration': duration,
                'sample_rate': sr,
                'speech_rate': speech_rate,
                **pitch_features,
                **intensity_features,
                **spectral_features
            }
            
            return {
                'status': 'success',
                'features': analysis_results,
                'insights': self._generate_insights(analysis_results)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error_message': str(e),
                'features': {},
                'insights': ''
            }
    
    def _generate_insights(self, features: Dict) -> str:
        """
        Generate human-readable insights from features
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            String with insights
        """
        insights = []
        
        # Duration insight
        duration = features.get('duration', 0)
        insights.append(f"Recording duration: {duration:.2f} seconds")
        
        # Pitch insights
        pitch_mean = features.get('pitch_mean', 0)
        if pitch_mean > 0:
            if pitch_mean < 150:
                pitch_desc = "low pitch (typical for male voices)"
            elif pitch_mean < 250:
                pitch_desc = "moderate pitch"
            else:
                pitch_desc = "high pitch (typical for female voices)"
            insights.append(f"Average pitch: {pitch_mean:.1f} Hz ({pitch_desc})")
        
        # Intensity insight
        intensity_mean = features.get('intensity_mean', 0)
        if intensity_mean > 0.1:
            insights.append(f"Good vocal intensity detected")
        else:
            insights.append(f"Low vocal intensity - consider speaking louder")
        
        # Speech rate insight
        speech_rate = features.get('speech_rate', 0)
        if speech_rate > 0:
            if speech_rate < 2:
                rate_desc = "slow and deliberate"
            elif speech_rate < 4:
                rate_desc = "moderate pace"
            else:
                rate_desc = "fast-paced"
            insights.append(f"Speech rate: {rate_desc} ({speech_rate:.1f} syllables/sec)")
        
        return " | ".join(insights)


def process_audio_file(file_path: str) -> Dict:
    """
    Convenience function to process an audio file
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Dictionary with analysis results
    """
    processor = AudioProcessor()
    return processor.analyze_audio(file_path)
