import api from './api';

export const authService = {
    async login(email, password) {
        const response = await api.post('/auth/login', { email, password });
        return response.data;
    },

    async register(email, password, name, orgName = null) {
        const response = await api.post('/auth/register', {
            email,
            password,
            name,
            org_name: orgName
        });
        return response.data;
    },

    async getMe() {
        const response = await api.get('/auth/me');
        return response.data;
    },

    async updateProfile(data) {
        const response = await api.put('/auth/me', data);
        return response.data;
    },

    async refreshToken(refreshToken) {
        const response = await api.post('/auth/refresh', {
            refresh_token: refreshToken
        });
        return response.data;
    }
};
