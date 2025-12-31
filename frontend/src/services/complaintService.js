import api from './api';

export const complaintService = {
    async getComplaints(params = {}) {
        const response = await api.get('/complaints', { params });
        return response.data;
    },

    async getComplaint(id) {
        const response = await api.get(`/complaints/${id}`);
        return response.data;
    },

    async createComplaint(data) {
        const response = await api.post('/complaints', data);
        return response.data;
    },

    async updateComplaint(id, data) {
        const response = await api.put(`/complaints/${id}`, data);
        return response.data;
    },

    async deleteComplaint(id) {
        await api.delete(`/complaints/${id}`);
    },

    async bulkOperation(data) {
        const response = await api.post('/complaints/bulk', data);
        return response.data;
    },

    async simulateEmail(data) {
        const response = await api.post('/emails/simulate', data);
        return response.data;
    }
};
