import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const getAdminHeaders = () => ({
  'x-api-key': localStorage.getItem('adminKey') || 'admin123'
});

export const checkHealth = async () => {
  try {
    const res = await api.get('/');
    return res.status === 200;
  } catch (e) {
    return false;
  }
};

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
  // Pass analysis_id if available (it might be in data or we need to add it)
  // The data object structure depends on the caller.
  const response = await api.post(`/feedback/${endpoint}`, data);
  return response.data;
};

// Admin API
export const adminApi = {
  getFeedback: async (params: any = {}) => {
    const res = await api.get('/admin/feedback', { params, headers: getAdminHeaders() });
    return res.data;
  },
  updateFeedbackStatus: async (id: number, status: string) => {
    const res = await api.patch(`/admin/feedback/${id}/status`, null, {
      params: { status },
      headers: getAdminHeaders()
    });
    return res.data;
  },
  syncToChroma: async (id: number) => {
    const res = await api.post(`/admin/feedback/${id}/sync`, {}, { headers: getAdminHeaders() });
    return res.data;
  },
  batchSync: async (adminKey: string) => {
    const res = await api.post(`/admin/feedback/sync-batch`, null, {
      params: { admin_key: adminKey },
      headers: getAdminHeaders()
    });
    return res.data;
  },
  exportCsv: async () => {
    const res = await api.get('/admin/export/csv', {
      headers: getAdminHeaders(),
      responseType: 'blob'
    });
    return res.data;
  }
};

export default api;