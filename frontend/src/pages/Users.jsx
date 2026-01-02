import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { userService } from '../services/userService';
import { departmentService } from '../services/departmentService';
import Layout from '../components/common/Layout';
import { CreateUserModal } from '../components/common/Modals';
import { Mail, Building, Shield, AlertCircle, CheckCircle, Plus, Search, Filter, X, ArrowUpDown } from 'lucide-react';

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
        department_id: '',
        status: ''
    });
    const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });

    // Debounce Search
    useEffect(() => {
        const timer = setTimeout(() => {
            fetchUsers();
        }, 500);

        return () => clearTimeout(timer);
    }, [search, filters, sortConfig]);

    // Fetch Departments for Filter
    useEffect(() => {
        loadDepartments();
    }, []);

    const loadDepartments = async () => {
        try {
            if (currentUser?.org_id) {
                const data = await departmentService.getAll(currentUser.org_id);
                setDepartments(data || []);
            }
        } catch (err) {
            console.error(err);
        }
    };

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const params = {
                ...filters,
                search: search || undefined, // Only send if not empty
                sort_by: sortConfig.key,
                sort_order: sortConfig.direction
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
        setFilters({ role: '', department_id: '', status: '' });
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
        <div className="space-y-6 animate-fade-in">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">User Management</h1>
                    <p className="mt-1 text-sm text-slate-500">
                        Manage users, roles, and department assignments
                    </p>
                </div>
                <button
                    onClick={() => setShowModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors shadow-sm shadow-blue-600/20"
                >
                    <Plus className="w-4 h-4" />
                    <span>Create User</span>
                </button>
            </div>

            {/* Search & Filters */}
            <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-4 md:space-y-0 md:flex md:items-center md:gap-4 shadow-sm">
                <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input
                        type="text"
                        placeholder="Search users by name or email..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-10 pr-4 py-2 text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                    />
                </div>

                <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0">
                    <select
                        value={filters.role}
                        onChange={(e) => handleFilterChange('role', e.target.value)}
                        className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                    >
                        <option value="">All Roles</option>
                        <option value="admin">Admin</option>
                        <option value="manager">Manager</option>
                        <option value="agent">Agent</option>
                    </select>

                    <select
                        value={filters.department_id}
                        onChange={(e) => handleFilterChange('department_id', e.target.value)}
                        className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                    >
                        <option value="">All Departments</option>
                        {departments.map(d => (
                            <option key={d.department_id} value={d.department_id}>{d.name}</option>
                        ))}
                    </select>

                    <select
                        value={filters.status}
                        onChange={(e) => handleFilterChange('status', e.target.value)}
                        className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                    >
                        <option value="">All Status</option>
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                    </select>

                    <div className="relative">
                        <select
                            value={`${sortConfig.key}-${sortConfig.direction}`}
                            onChange={(e) => {
                                const [key, direction] = e.target.value.split('-');
                                setSortConfig({ key, direction });
                            }}
                            className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all pl-9 appearance-none"
                        >
                            <option value="created_at-desc">Newest First</option>
                            <option value="name-asc">Name (A-Z)</option>
                            <option value="name-desc">Name (Z-A)</option>
                        </select>
                        <ArrowUpDown className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                    </div>

                    {(search || filters.role || filters.department_id || filters.status) && (
                        <button
                            onClick={clearFilters}
                            className="p-2 text-slate-400 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
                            title="Clear Filters"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    )}
                </div>
            </div>

            {loading ? (
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <p className="text-slate-500">Loading users...</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {Array.isArray(users) && users.map((u) => (
                        <div
                            key={u.user_id}
                            onClick={() => navigate(`/users/${u.user_id}`)}
                            className="bg-white border border-slate-200 rounded-xl p-6 hover:border-blue-500/50 hover:shadow-md transition-all group cursor-pointer"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center text-blue-600 font-bold text-lg border border-blue-100">
                                        {u.name.charAt(0).toUpperCase()}
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors">{u.name}</h3>
                                        <div className="flex items-center gap-1 text-slate-500 text-xs">
                                            <Mail className="w-3 h-3" />
                                            <span className="truncate max-w-[150px]">{u.email}</span>
                                        </div>
                                    </div>
                                </div>
                                <span className={`px-2 py-1 rounded-full text-xs font-medium border uppercase ${u.role === 'admin' ? 'bg-purple-50 text-purple-600 border-purple-200' :
                                    u.role === 'manager' ? 'bg-blue-50 text-blue-600 border-blue-200' :
                                        'bg-emerald-50 text-emerald-600 border-emerald-200'
                                    }`}>
                                    {u.role}
                                </span>
                            </div>

                            <div className="space-y-3 mb-6">
                                <div className="flex items-center justify-between text-sm">
                                    <div className="flex items-center gap-2 text-slate-400">
                                        <Building className="w-4 h-4" />
                                        <span>Department</span>
                                    </div>
                                    <span className="text-slate-700 font-medium">{u.department_name || 'N/A'}</span>
                                </div>
                                {(u.team || u.team_name) && (
                                    <div className="flex items-center justify-between text-sm">
                                        <div className="flex items-center gap-2 text-slate-400">
                                            <Shield className="w-4 h-4" />
                                            <span>Team</span>
                                        </div>
                                        <span className="text-slate-700 font-medium">{u.team || u.team_name}</span>
                                    </div>
                                )}
                            </div>

                            <div className="grid grid-cols-2 gap-3 pt-4 border-t border-slate-100">
                                <div className="bg-red-50 rounded-lg p-2 text-center border border-red-100">
                                    <div className="flex items-center justify-center gap-1 text-red-600 text-xs mb-1 font-medium">
                                        <AlertCircle className="w-3 h-3" />
                                        <span>Escalations</span>
                                    </div>
                                    <span className="text-lg font-bold text-red-600">{u.escalations_count || 0}</span>
                                </div>
                                <div className="bg-emerald-50 rounded-lg p-2 text-center border border-emerald-100">
                                    <div className="flex items-center justify-center gap-1 text-emerald-600 text-xs mb-1 font-medium">
                                        <CheckCircle className="w-3 h-3" />
                                        <span>Resolutions</span>
                                    </div>
                                    <span className="text-lg font-bold text-emerald-600">{u.resolutions_count || 0}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                    {(!users || users.length === 0) && (
                        <div className="col-span-full text-center py-12">
                            <div className="mx-auto w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center text-slate-400 mb-3">
                                <Search className="w-6 h-6" />
                            </div>
                            <h3 className="text-slate-900 font-medium mb-1">No users found</h3>
                            <p className="text-slate-500 text-sm">Try adjusting your filters or search terms</p>
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
