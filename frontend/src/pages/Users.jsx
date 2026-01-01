import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { userService } from '../services/userService';
import { departmentService } from '../services/departmentService';
import Layout from '../components/common/Layout';
import { CreateUserModal } from '../components/common/Modals';
import { Mail, Building, Shield, AlertCircle, CheckCircle, Plus } from 'lucide-react';

// Simple Error Boundary
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }
    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }
    componentDidCatch(error, errorInfo) {
        console.error("ErrorBoundary caught error:", error, errorInfo);
    }
    render() {
        if (this.state.hasError) {
            return (
                <div className="p-8 text-black bg-red-100 border border-red-400 rounded">
                    <h2 className="text-xl font-bold mb-2">Something went wrong!</h2>
                    <p className="font-mono text-sm whitespace-pre-wrap">
                        {this.state.error?.toString()}
                    </p>
                </div>
            );
        }
        return this.props.children;
    }
}

export default function Users() {
    const navigate = useNavigate();
    return (
        <ErrorBoundary>
            <UsersContent navigate={navigate} />
        </ErrorBoundary>
    );
}

import { Search, Filter, X } from 'lucide-react';

// ... (keep props and imports same)

function UsersContent({ navigate }) {
    const { user: currentUser } = useAuth();
    const [users, setUsers] = useState([]);
    const [departments, setDepartments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);

    // Filters State
    const [search, setSearch] = useState('');
    const [filters, setFilters] = useState({
        role: '',
        department: '',
        status: ''
    });

    // Debounce Search
    useEffect(() => {
        const timer = setTimeout(() => {
            fetchUsers();
        }, 500);

        return () => clearTimeout(timer);
    }, [search, filters]);

    // Fetch Departments for Filter
    useEffect(() => {
        loadDepartments();
    }, []);

    const loadDepartments = async () => {
        try {
            const data = await departmentService.getDepartments();
            setDepartments(data || []);
        } catch (err) {
            console.error(err);
        }
    };

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const params = {
                ...filters,
                search: search || undefined // Only send if not empty
            };
            // Clean empty filters
            Object.keys(params).forEach(key => !params[key] && delete params[key]);

            const data = await userService.getUsers(params);
            console.log("Fetched users:", data);
            setUsers(data?.items || []);
        } catch (err) {
            console.error(err);
            setUsers([]);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateUser = async (formData) => {
        try {
            await userService.createUser(formData);
            setShowModal(false);
            fetchUsers();
        } catch (err) {
            console.error("Failed to create user", err);
            alert("Failed to create user: " + (err.response?.data?.detail || err.message));
        }
    };

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const clearFilters = () => {
        setSearch('');
        setFilters({ role: '', department: '', status: '' });
    };

    const isAdmin = currentUser?.role === 'admin' || currentUser?.role === 'ADMIN';

    if (!currentUser || !isAdmin) {
        return (
            <Layout>
                <div className="p-8 text-center text-red-500">
                    Access Denied. Admin only.
                </div>
            </Layout>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Manage users, roles, and department assignments
                    </p>
                </div>
                <button
                    onClick={() => setShowModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 font-medium transition-colors"
                >
                    <Plus className="w-4 h-4" />
                    <span>Create User</span>
                </button>
            </div>

            {/* Search & Filters */}
            <div className="bg-[#1e293b] border border-white/5 rounded-xl p-4 space-y-4 md:space-y-0 md:flex md:items-center md:gap-4">
                <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search users by name or email..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full bg-black/20 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-primary-500/50"
                    />
                </div>

                <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0">
                    <select
                        value={filters.role}
                        onChange={(e) => handleFilterChange('role', e.target.value)}
                        className="bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-primary-500/50"
                    >
                        <option value="">All Roles</option>
                        <option value="admin">Admin</option>
                        <option value="manager">Manager</option>
                        <option value="agent">Agent</option>
                    </select>

                    <select
                        value={filters.department}
                        onChange={(e) => handleFilterChange('department', e.target.value)}
                        className="bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-primary-500/50"
                    >
                        <option value="">All Departments</option>
                        {departments.map(d => (
                            <option key={d.name} value={d.name}>{d.name}</option>
                        ))}
                    </select>

                    <select
                        value={filters.status}
                        onChange={(e) => handleFilterChange('status', e.target.value)}
                        className="bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-primary-500/50"
                    >
                        <option value="">All Status</option>
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                    </select>

                    {(search || filters.role || filters.department || filters.status) && (
                        <button
                            onClick={clearFilters}
                            className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                            title="Clear Filters"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    )}
                </div>
            </div>

            {loading ? (
                <div className="text-center py-8">Loading...</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {Array.isArray(users) && users.map((u) => (
                        <div
                            key={u.user_id}
                            onClick={() => navigate(`/users/${u.user_id}`)}
                            className="bg-[#1e293b] border border-white/5 rounded-xl p-6 hover:border-primary-500/50 transition-all group cursor-pointer"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full bg-primary-500/20 flex items-center justify-center text-primary-400 font-bold text-lg">
                                        {u.name.charAt(0).toUpperCase()}
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-white group-hover:text-primary-400 transition-colors">{u.name}</h3>
                                        <div className="flex items-center gap-1 text-gray-400 text-xs">
                                            <Mail className="w-3 h-3" />
                                            <span className="truncate max-w-[150px]">{u.email}</span>
                                        </div>
                                    </div>
                                </div>
                                <span className={`px-2 py-1 rounded-full text-xs font-medium border uppercase ${u.role === 'admin' ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' :
                                    u.role === 'manager' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                                        'bg-green-500/10 text-green-400 border-green-500/20'
                                    }`}>
                                    {u.role}
                                </span>
                            </div>

                            <div className="space-y-3 mb-6">
                                <div className="flex items-center justify-between text-sm">
                                    <div className="flex items-center gap-2 text-gray-400">
                                        <Building className="w-4 h-4" />
                                        <span>Department</span>
                                    </div>
                                    <span className="text-gray-200">{u.department_name || 'N/A'}</span>
                                </div>
                                {(u.team || u.team_name) && (
                                    <div className="flex items-center justify-between text-sm">
                                        <div className="flex items-center gap-2 text-gray-400">
                                            <Shield className="w-4 h-4" />
                                            <span>Team</span>
                                        </div>
                                        <span className="text-gray-200">{u.team || u.team_name}</span>
                                    </div>
                                )}
                            </div>

                            <div className="grid grid-cols-2 gap-3 pt-4 border-t border-white/5">
                                <div className="bg-red-500/5 rounded-lg p-2 text-center border border-red-500/10">
                                    <div className="flex items-center justify-center gap-1 text-red-400 text-xs mb-1">
                                        <AlertCircle className="w-3 h-3" />
                                        <span>Escalations</span>
                                    </div>
                                    <span className="text-lg font-bold text-red-400">{u.escalations_count || 0}</span>
                                </div>
                                <div className="bg-green-500/5 rounded-lg p-2 text-center border border-green-500/10">
                                    <div className="flex items-center justify-center gap-1 text-green-400 text-xs mb-1">
                                        <CheckCircle className="w-3 h-3" />
                                        <span>Resolutions</span>
                                    </div>
                                    <span className="text-lg font-bold text-green-400">{u.resolutions_count || 0}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                    {(!users || users.length === 0) && (
                        <div className="col-span-full text-center py-12 text-gray-500">
                            No users found.
                        </div>
                    )}
                </div>
            )}

            <CreateUserModal
                isOpen={showModal}
                onClose={() => setShowModal(false)}
                onCreate={handleCreateUser}
            />
        </div>
    );
}
