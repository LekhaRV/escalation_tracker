import api from './api';

export const analyticsService = {
    async getAnalytics(type = 'dashboard', params = {}) {
        const response = await api.get('/analytics', { params: { type, ...params } });
        return response.data;
    },

    async getWorkload() {
        const response = await api.get('/analytics/workload');
        return response.data;
    },

    async getEscalations() {
        const response = await api.get('/analytics/escalations');
        return response.data;
    },

    async getSmartInsights() {
        const response = await api.get('/analytics/smart-insights');
        return response.data;
    },

    async getPatterns() {
        const response = await api.get('/analytics', { params: { type: 'patterns' } });
        return response.data;
    },

    async getInsights() {
        const response = await api.get('/analytics', { params: { type: 'insights' } });
        return response.data;
    }
};
