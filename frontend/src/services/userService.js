import api from './api';

export const userService = {
    async getUsers(params) {
        const response = await api.get('/admin/users', { params });
        return response.data;
    },

    async getUser(userId) {
        const response = await api.get(`/admin/users/${userId}`);
        return response.data;
    },

    async createUser(data) {
        const response = await api.post('/admin/users', data);
        return response.data;
    },

    async updateUser(userId, data) {
        const response = await api.put(`/admin/users/${userId}`, data);
        return response.data;
    }
};
