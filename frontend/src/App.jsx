import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Complaints from './pages/Complaints';
import ComplaintDetail from './pages/ComplaintDetail';
import Projects from './pages/Projects';
import ProjectDetail from './pages/ProjectDetail';
import Departments from './pages/Departments';
import Settings from './pages/Settings';
import Users from './pages/Users';
import UserDetail from './pages/UserDetail';
import Layout from './components/common/Layout';

// Protected Route wrapper
function ProtectedRoute({ children, roles = [] }) {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
            </div>
        );
    }

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    if (roles.length > 0 && !roles.includes(user.role)) {
        return <Navigate to="/" replace />;
    }

    return children;
}

function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Routes>
                    <Route path="/login" element={<Login />} />

                    <Route path="/" element={
                        <ProtectedRoute>
                            <Layout />
                        </ProtectedRoute>
                    }>
                        <Route index element={<Dashboard />} />
                        <Route path="complaints" element={<Complaints />} />
                        <Route path="complaints/:id" element={<ComplaintDetail />} />
                        <Route path="projects" element={<Projects />} />
                        <Route path="projects/:id" element={<ProjectDetail />} />
                        <Route path="departments" element={<Departments />} />

                        <Route path="settings" element={
                            <ProtectedRoute roles={['ADMIN']}>
                                <Settings />
                            </ProtectedRoute>
                        } />
                        <Route path="users" element={
                            <ProtectedRoute roles={['ADMIN']}>
                                <Users />
                            </ProtectedRoute>
                        } />
                        <Route path="users/:id" element={
                            <ProtectedRoute roles={['ADMIN']}>
                                <UserDetail />
                            </ProtectedRoute>
                        } />
                    </Route>

                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}

export default App;
