import api from './api';

export const analyticsService = {
    async getAnalytics(type = 'dashboard', params = {}) {
        const response = await api.get('/analytics', { params: { type, ...params } });
        return response.data;
    },

    async exportData(data) {
        const response = await api.post('/analytics/export', data);
        return response.data;
    },

    async getRealtime() {
        const response = await api.get('/analytics/realtime');
        return response.data;
    },

    async getReport(type) {
        const response = await api.get(`/analytics/reports/${type}`);
        return response.data;
    },

    async askAnalyst(query) {
        const response = await api.post('/analytics/ask', { query });
        return response.data;
    }
};
