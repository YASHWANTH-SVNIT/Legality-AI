import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadContract = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/analyze/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getAnalysisStatus = async (analysisId: string) => {
  const response = await api.get(`/analyze/${analysisId}/status`);
  return response.data;
};

export const getAnalysisResults = async (analysisId: string) => {
  const response = await api.get(`/analyze/${analysisId}/results`);
  return response.data;
};

export const submitFeedback = async (
  endpoint: 'false-positive' | 'false-negative' | 'approve-fix',
  data: any
) => {
  const response = await api.post(`/feedback/${endpoint}`, data);
  return response.data;
};

export default api;