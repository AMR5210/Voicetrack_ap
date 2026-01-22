// API Configuration and Service
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

// API Base URL - Using production for mobile testing
const API_BASE_URL = Platform.OS === 'web'
  ? 'http://localhost:8000/api'  // Web browser uses local
  : 'https://voicetrack-app.ue.r.appspot.com/api';  // Mobile uses production

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and we haven't retried yet, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await AsyncStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          await AsyncStorage.setItem('accessToken', access);

          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        await AsyncStorage.multiRemove(['accessToken', 'refreshToken', 'user']);
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  register: async (userData) => {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  login: async (credentials) => {
    const response = await api.post('/auth/login/', credentials);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me/');
    return response.data;
  },

  logout: async () => {
    await AsyncStorage.multiRemove(['accessToken', 'refreshToken', 'user']);
  },
};

// Recordings API calls
export const recordingsAPI = {
  getAll: async () => {
    const response = await api.get('/recordings/');
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/recordings/${id}/`);
    return response.data;
  },

  create: async (formData) => {
    const response = await api.post('/recordings/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for file upload
    });
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/recordings/${id}/`);
    return response.data;
  },

  getAnalysis: async (id) => {
    const response = await api.get(`/recordings/${id}/analysis/`);
    return response.data;
  },

  triggerAnalysis: async (id) => {
    const response = await api.post(`/recordings/${id}/trigger_analysis/`);
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/recordings/stats/');
    return response.data;
  },
};

// Health check
export const healthCheck = async () => {
  try {
    const response = await api.get('/health/');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    return null;
  }
};

export default api;
