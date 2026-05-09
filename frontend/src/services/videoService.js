import api from './api';

const videoService = {
  /**
   * Uploads a video file to the backend.
   * @param {File} file - The video file to upload.
   * @param {string} title - The title of the video.
   * @param {string} subjectName - The subject name (optional).
   * @param {string} uploadedBy - The user identifier (optional).
   * @returns {Promise<Object>} - The response from the backend.
   */
  uploadVideo: async (file, title, subjectName = '', uploadedBy = '') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    if (subjectName) formData.append('subject_name', subjectName);
    if (uploadedBy) formData.append('uploaded_by', uploadedBy);

    try {
      const response = await api.post('/api/upload-video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Video upload error:', error);
      throw error.response?.data?.detail || 'Video upload failed. Please try again.';
    }
  },

  /**
   * Fetches the list of videos (if such endpoint exists later).
   */
  // getVideos: async () => { ... }
};

export default videoService;
