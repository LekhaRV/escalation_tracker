import api from './api';

export const departmentService = {
    async getAll(orgId) {
        const response = await api.get(`/departments?org_id=${orgId}`);
        return response.data;
    },

    async create(data) {
        const response = await api.post('/departments', data);
        return response.data;
    }
};
