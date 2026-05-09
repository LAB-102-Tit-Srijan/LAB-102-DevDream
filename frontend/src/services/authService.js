import api from './api';

const authService = {
  login: async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Login failed. Please check your credentials.';
    }
  },

  signup: async (email, password) => {
    try {
      const response = await api.post('/auth/signup', { email, password });
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Signup failed. Please try again.';
    }
  },

  getProfile: async () => {
    try {
      const response = await api.get('/protected');
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Failed to fetch profile.';
    }
  }
};

export default authService;
