import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  TextInput,
} from 'react-native';
import { Audio } from 'expo-av';
import { recordingsAPI } from '../services/api';

export default function RecordScreen({ navigation }) {
  const [recording, setRecording] = useState(null);
  const [recordingURI, setRecordingURI] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [duration, setDuration] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [title, setTitle] = useState('');
  const [sound, setSound] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    return sound
      ? () => {
          sound.unloadAsync();
        }
      : undefined;
  }, [sound]);

  const requestPermissions = async () => {
    try {
      const permission = await Audio.requestPermissionsAsync();
      if (!permission.granted) {
        Alert.alert('Permission Required', 'Please grant microphone permissions to record audio');
        return false;
      }
      return true;
    } catch (error) {
      console.error('Permission error:', error);
      return false;
    }
  };

  const startRecording = async () => {
    try {
      const hasPermission = await requestPermissions();
      if (!hasPermission) return;

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );

      setRecording(recording);
      setIsRecording(true);
      setDuration(0);

      // Update duration every second
      const interval = setInterval(() => {
        setDuration((prev) => prev + 1);
      }, 1000);

      recording._interval = interval;
    } catch (error) {
      console.error('Failed to start recording:', error);
      Alert.alert('Error', 'Failed to start recording');
    }
  };

  const pauseRecording = async () => {
    if (recording) {
      await recording.pauseAsync();
      setIsPaused(true);
      clearInterval(recording._interval);
    }
  };

  const resumeRecording = async () => {
    if (recording) {
      await recording.startAsync();
      setIsPaused(false);
      
      const interval = setInterval(() => {
        setDuration((prev) => prev + 1);
      }, 1000);
      recording._interval = interval;
    }
  };

  const stopRecording = async () => {
    if (!recording) return;

    try {
      clearInterval(recording._interval);
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecordingURI(uri);
      setRecording(null);
      setIsRecording(false);
      setIsPaused(false);

      console.log('Recording saved to:', uri);
    } catch (error) {
      console.error('Error stopping recording:', error);
    }
  };

  const playRecording = async () => {
    if (!recordingURI) return;

    try {
      if (isPlaying && sound) {
        await sound.pauseAsync();
        setIsPlaying(false);
      } else if (sound) {
        await sound.playAsync();
        setIsPlaying(true);
      } else {
        const { sound: newSound } = await Audio.Sound.createAsync(
          { uri: recordingURI },
          { shouldPlay: true }
        );
        
        newSound.setOnPlaybackStatusUpdate((status) => {
          if (status.didJustFinish) {
            setIsPlaying(false);
          }
        });

        setSound(newSound);
        setIsPlaying(true);
      }
    } catch (error) {
      console.error('Error playing recording:', error);
      Alert.alert('Error', 'Failed to play recording');
    }
  };

  const deleteRecording = () => {
    Alert.alert(
      'Delete Recording',
      'Are you sure you want to delete this recording?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => {
            setRecordingURI(null);
            setDuration(0);
            setTitle('');
            if (sound) {
              sound.unloadAsync();
              setSound(null);
            }
            setIsPlaying(false);
          },
        },
      ]
    );
  };

  const uploadRecording = async () => {
    if (!recordingURI) {
      Alert.alert('Error', 'No recording to upload');
      return;
    }

    if (!title.trim()) {
      Alert.alert('Error', 'Please enter a title for your recording');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('title', title.trim());
      formData.append('audio_file', {
        uri: recordingURI,
        type: 'audio/m4a',
        name: `recording_${Date.now()}.m4a`,
      });

      await recordingsAPI.create(formData);

      Alert.alert(
        'Success',
        'Recording uploaded successfully!',
        [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]
      );
    } catch (error) {
      console.error('Upload error:', error);
      Alert.alert('Upload Failed', 'Failed to upload recording. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backButton}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Record Audio</Text>
        <View style={{ width: 50 }} />
      </View>

      {/* Content */}
      <View style={styles.content}>
        {/* Microphone Visual */}
        <View style={[styles.micContainer, isRecording && styles.micRecording]}>
          <Text style={styles.micIcon}>🎤</Text>
        </View>

        {/* Duration */}
        <Text style={styles.duration}>{formatDuration(duration)}</Text>

        {/* Status */}
        {isRecording && (
          <Text style={styles.status}>
            {isPaused ? 'Paused' : 'Recording...'}
          </Text>
        )}

        {recordingURI && !isRecording && (
          <Text style={styles.status}>Recording Complete!</Text>
        )}

        {/* Recording Controls */}
        <View style={styles.controls}>
          {!isRecording && !recordingURI && (
            <TouchableOpacity
              style={styles.recordButton}
              onPress={startRecording}
            >
              <Text style={styles.recordButtonText}>Start Recording</Text>
            </TouchableOpacity>
          )}

          {isRecording && (
            <View style={styles.controlRow}>
              <TouchableOpacity
                style={styles.controlButton}
                onPress={isPaused ? resumeRecording : pauseRecording}
              >
                <Text style={styles.controlButtonText}>
                  {isPaused ? '▶️ Resume' : '⏸ Pause'}
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.controlButton, styles.stopButton]}
                onPress={stopRecording}
              >
                <Text style={styles.controlButtonText}>⏹ Stop</Text>
              </TouchableOpacity>
            </View>
          )}

          {recordingURI && !isRecording && (
            <>
              {/* Title Input */}
              <TextInput
                style={styles.titleInput}
                placeholder="Enter recording title"
                value={title}
                onChangeText={setTitle}
              />

              {/* Playback Controls */}
              <View style={styles.controlRow}>
                <TouchableOpacity
                  style={styles.controlButton}
                  onPress={playRecording}
                >
                  <Text style={styles.controlButtonText}>
                    {isPlaying ? '⏸ Pause' : '▶️ Play'}
                  </Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.controlButton, styles.deleteButton]}
                  onPress={deleteRecording}
                >
                  <Text style={styles.controlButtonText}>🗑️ Delete</Text>
                </TouchableOpacity>
              </View>

              {/* Upload Button */}
              <TouchableOpacity
                style={[styles.uploadButton, uploading && styles.uploadButtonDisabled]}
                onPress={uploadRecording}
                disabled={uploading}
              >
                {uploading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <Text style={styles.uploadButtonText}>Upload Recording</Text>
                )}
              </TouchableOpacity>
            </>
          )}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#2196F3',
    padding: 20,
    paddingTop: 50,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  backButton: {
    color: '#fff',
    fontSize: 18,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  micContainer: {
    width: 150,
    height: 150,
    borderRadius: 75,
    backgroundColor: '#2196F3',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  micRecording: {
    backgroundColor: '#f44336',
  },
  micIcon: {
    fontSize: 80,
  },
  duration: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  status: {
    fontSize: 18,
    color: '#666',
    marginBottom: 30,
  },
  controls: {
    width: '100%',
    alignItems: 'center',
  },
  recordButton: {
    backgroundColor: '#f44336',
    paddingHorizontal: 40,
    paddingVertical: 15,
    borderRadius: 8,
  },
  recordButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  controlRow: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 15,
  },
  controlButton: {
    backgroundColor: '#2196F3',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    flex: 1,
  },
  stopButton: {
    backgroundColor: '#f44336',
  },
  deleteButton: {
    backgroundColor: '#757575',
  },
  controlButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  titleInput: {
    width: '100%',
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    fontSize: 16,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  uploadButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 40,
    paddingVertical: 15,
    borderRadius: 8,
    width: '100%',
    alignItems: 'center',
  },
  uploadButtonDisabled: {
    opacity: 0.6,
  },
  uploadButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
