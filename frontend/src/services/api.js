// src/services/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🔄 API Call: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Success: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.error || `Server error: ${error.response.status}`;
      throw new Error(message);
    } else if (error.request) {
      // Request made but no response received
      throw new Error('Network error: Could not connect to server. Please ensure the backend is running on port 5000.');
    } else {
      // Something else happened
      throw new Error('Request configuration error');
    }
  }
);

export const analyzeAsteroid = async (asteroidId) => {
  try {
    const response = await api.post('/full_analysis', {
      asteroid_id: asteroidId
    });
    return response.data;
  } catch (error) {
    console.error('Asteroid analysis failed:', error);
    throw error;
  }
};

export const simulateDeflection = async (deflectionParams) => {
  try {
    const response = await api.post('/recalculate_trajectory', deflectionParams);
    return response.data;
  } catch (error) {
    console.error('Deflection simulation failed:', error);
    throw error;
  }
};

export const generatePDF = async (missionPlan) => {
  try {
    const response = await api.post('/generate_pdf', missionPlan, {
      responseType: 'blob'
    });
    return response.data;
  } catch (error) {
    console.error('PDF generation failed:', error);
    throw error;
  }
};

export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

export const sendChatMessage = async (message, missionContext = null) => {
  try {
    const response = await api.post('/chat', {
      message: message,
      mission_context: missionContext
    });
    return response.data;
  } catch (error) {
    console.error('Chat message failed:', error);
    throw error;
  }
};

export default api;