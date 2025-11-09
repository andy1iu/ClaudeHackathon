import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const patientsApi = {
  getAll: async () => {
    const response = await api.get('/patients');
    return response.data;
  },

  getNarratives: async (patientId) => {
    const response = await api.get(`/patients/${patientId}/narratives`);
    return response.data;
  },

  getBriefing: async (patientId) => {
    const response = await api.get(`/patients/${patientId}/briefing`);
    return response.data;
  },

  getEHR: async (patientId) => {
    const response = await api.get(`/patients/${patientId}/ehr`);
    return response.data;
  },

  synthesizeBriefing: async (patientId, narrative) => {
    const response = await api.post('/synthesize', {
      patient_id: patientId,
      narrative: narrative,
    });
    return response.data;
  },
};

export const chatApi = {
  startChat: async (patientId) => {
    const response = await api.post('/chat/start', {
      patient_id: patientId,
    });
    return response.data;
  },

  continueChat: async (conversationId, userMessage) => {
    const response = await api.post('/chat/continue', {
      conversation_id: conversationId,
      user_message: userMessage,
    });
    return response.data;
  },
};

export const appointmentsApi = {
  getAll: async (params = {}) => {
    const response = await api.get('/appointments', { params });
    return response.data;
  },

  getById: async (appointmentId) => {
    const response = await api.get(`/appointments/${appointmentId}`);
    return response.data;
  },

  getByPatient: async (patientId, options = {}) => {
    const params = { ...options };
    const response = await api.get(`/patients/${patientId}/appointments`, { params });
    return response.data;
  },

  getNextUpcoming: async (patientId = null) => {
    const params = patientId ? { patient_id: patientId } : {};
    const response = await api.get('/appointments/next/upcoming', { params });
    return response.data;
  },

  create: async (appointmentData) => {
    const response = await api.post('/appointments', appointmentData);
    return response.data;
  },

  update: async (appointmentId, appointmentData) => {
    const response = await api.put(`/appointments/${appointmentId}`, appointmentData);
    return response.data;
  },

  delete: async (appointmentId) => {
    const response = await api.delete(`/appointments/${appointmentId}`);
    return response.data;
  },
};

export default api;
