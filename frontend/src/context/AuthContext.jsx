import { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkAuth();
    }, []);

    async function checkAuth() {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const userData = await authService.getMe();
                setUser(userData);
            } catch (error) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
            }
        }
        setLoading(false);
    }

    async function login(email, password) {
        const tokens = await authService.login(email, password);
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
        const userData = await authService.getMe();
        setUser(userData);
        return userData;
    }

    async function register(email, password, name, orgName) {
        const result = await authService.register(email, password, name, orgName);
        localStorage.setItem('access_token', result.tokens.access_token);
        localStorage.setItem('refresh_token', result.tokens.refresh_token);
        setUser(result.user);
        return result.user;
    }

    function logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
    }

    const value = {
        user,
        loading,
        login,
        register,
        logout,
        isAdmin: user?.role === 'admin',
        isManager: user?.role === 'manager' || user?.role === 'admin',
        isAgent: ['admin', 'manager', 'agent'].includes(user?.role)
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
