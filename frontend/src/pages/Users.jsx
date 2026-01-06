import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { userService } from '../services/userService';
import { departmentService } from '../services/departmentService';
import Layout from '../components/common/Layout';
import { CreateUserModal } from '../components/common/Modals';
import { Mail, Building, Shield, AlertCircle, CheckCircle, Plus, Search, Filter, X } from 'lucide-react';

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
                <div className="p-8 text-slate-800 bg-red-100 border border-red-300 rounded font-medium">
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
    const [page, setPage] = useState(1);
    const [pageSize] = useState(9);
    const [totalPages, setTotalPages] = useState(1);
    const [totalItems, setTotalItems] = useState(0);
    const [showModal, setShowModal] = useState(false);

    // Filters State
    const [search, setSearch] = useState('');
    const [filters, setFilters] = useState({
        role: '',
        department: '',
        status: ''
    });

    // Track if this is the first mount
    const isFirstMount = React.useRef(true);

    // Initial load
    useEffect(() => {
        fetchUsers(1);
        // After initial fetch, mark as no longer first mount
        isFirstMount.current = false;
    }, []);

    // Debounce Search and Filters - reset to page 1
    useEffect(() => {
        // Skip initial render
        const isInitial = search === '' && filters.role === '' && filters.department === '' && filters.status === '';
        if (isInitial) return;

        const timer = setTimeout(() => {
            setPage(1);
            fetchUsers(1);
        }, 500);

        return () => clearTimeout(timer);
    }, [search, filters]);

    // Fetch when page changes (skip only on initial mount, not when navigating back to page 1)
    useEffect(() => {
        if (!isFirstMount.current) {
            fetchUsers(page);
        }
    }, [page]);

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

    const fetchUsers = async (currentPage = page) => {
        try {
            setLoading(true);
            const params = {
                ...filters,
                search: search || undefined,
                page: currentPage,
                page_size: pageSize
            };
            // Clean empty filters
            Object.keys(params).forEach(key => !params[key] && delete params[key]);

            const data = await userService.getUsers(params);
            console.log("Fetched users:", data);
            setUsers(data?.items || []);
            setTotalPages(data?.total_pages || 1);
            setTotalItems(data?.total || 0);
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
            <div className="p-8 text-center text-red-600 bg-red-50 border border-red-200 rounded-lg">
                Access Denied. Admin only.
            </div>
        );
    }

    return (
        <div className="space-y-6 max-w-7xl mx-auto animate-fade-in">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
                        <Shield className="w-5 h-5 text-indigo-600" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-slate-800">User Management</h1>
                        <p className="text-sm text-slate-500">Manage users, roles, and department assignments</p>
                    </div>
                </div>
                <button
                    onClick={() => setShowModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-bold transition-colors shadow-sm"
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
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-10 pr-4 py-2 text-slate-900 placeholder-slate-400 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                    />
                </div>

                <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0">
                    <select
                        value={filters.role}
                        onChange={(e) => handleFilterChange('role', e.target.value)}
                        className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 font-medium focus:outline-none focus:border-primary-500"
                    >
                        <option value="">All Roles</option>
                        <option value="ADMIN">Admin</option>
                        <option value="MANAGER">Manager</option>
                        <option value="AGENT">Agent</option>
                    </select>

                    <select
                        value={filters.department}
                        onChange={(e) => handleFilterChange('department', e.target.value)}
                        className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 font-medium focus:outline-none focus:border-primary-500"
                    >
                        <option value="">All Departments</option>
                        {departments.map(d => (
                            <option key={d.name} value={d.name}>{d.name}</option>
                        ))}
                    </select>

                    <select
                        value={filters.status}
                        onChange={(e) => handleFilterChange('status', e.target.value)}
                        className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 font-medium focus:outline-none focus:border-primary-500"
                    >
                        <option value="">All Status</option>
                        <option value="ACTIVE">Active</option>
                        <option value="INACTIVE">Inactive</option>
                    </select>

                    {(search || filters.role || filters.department || filters.status) && (
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
                <div className="text-center py-12 text-slate-500 font-medium">Loading users...</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {Array.isArray(users) && users.map((u) => (
                        <div
                            key={u.user_id}
                            onClick={() => navigate(`/users/${u.user_id}`)}
                            className="bg-white border border-slate-200 rounded-xl p-6 hover:border-primary-400 transition-all group cursor-pointer shadow-sm hover:shadow-md"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold text-lg border border-primary-200">
                                        {u.name.charAt(0).toUpperCase()}
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-slate-900 group-hover:text-primary-700 transition-colors">{u.name}</h3>
                                        <div className="flex items-center gap-1 text-slate-500 text-xs font-medium">
                                            <Mail className="w-3 h-3" />
                                            <span className="truncate max-w-[150px]">{u.email}</span>
                                        </div>
                                    </div>
                                </div>
                                <span className={`px-2 py-1 rounded-full text-xs font-bold border uppercase ${u.role === 'admin' ? 'bg-purple-50 text-purple-700 border-purple-200' :
                                    u.role === 'manager' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                                        'bg-green-50 text-green-700 border-green-200'
                                    }`}>
                                    {u.role}
                                </span>
                            </div>

                            <div className="space-y-3 mb-6">
                                <div className="flex items-center justify-between text-sm">
                                    <div className="flex items-center gap-2 text-slate-500 font-medium">
                                        <Building className="w-4 h-4" />
                                        <span>Department</span>
                                    </div>
                                    <span className="text-slate-900 font-semibold">{u.department_name || 'N/A'}</span>
                                </div>
                                {(u.team || u.team_name) && (
                                    <div className="flex items-center justify-between text-sm">
                                        <div className="flex items-center gap-2 text-slate-500 font-medium">
                                            <Shield className="w-4 h-4" />
                                            <span>Team</span>
                                        </div>
                                        <span className="text-slate-900 font-semibold">{u.team || u.team_name}</span>
                                    </div>
                                )}
                            </div>

                            <div className="grid grid-cols-2 gap-3 pt-4 border-t border-slate-100">
                                <div className="bg-red-50 rounded-lg p-2 text-center border border-red-100">
                                    <div className="flex items-center justify-center gap-1 text-red-600 text-xs mb-1 font-bold uppercase">
                                        <AlertCircle className="w-3 h-3" />
                                        <span>Escalations</span>
                                    </div>
                                    <span className="text-lg font-bold text-red-700">{u.escalations_count || 0}</span>
                                </div>
                                <div className="bg-emerald-50 rounded-lg p-2 text-center border border-emerald-100">
                                    <div className="flex items-center justify-center gap-1 text-emerald-600 text-xs mb-1 font-bold uppercase">
                                        <CheckCircle className="w-3 h-3" />
                                        <span>Resolutions</span>
                                    </div>
                                    <span className="text-lg font-bold text-emerald-700">{u.resolutions_count || 0}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                    {(!users || users.length === 0) && (
                        <div className="col-span-full text-center py-12 text-slate-400 italic">
                            No users found matching your filters.
                        </div>
                    )}
                </div>
            )}

            {/* Pagination */}
            {!loading && users.length > 0 && (
                <div className="flex items-center justify-between border-t border-slate-200 pt-4">
                    <p className="text-sm text-muted">
                        Showing <span className="font-medium">{(page - 1) * pageSize + 1}</span> to <span className="font-medium">{Math.min(page * pageSize, totalItems)}</span> of <span className="font-medium">{totalItems}</span> users
                    </p>
                    <div className="flex gap-2">
                        <button
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                            disabled={page === 1}
                            className="px-3 py-1 text-sm font-medium text-algo bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            Previous
                        </button>
                        <button
                            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                            disabled={page === totalPages}
                            className="px-3 py-1 text-sm font-medium text-algo bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            Next
                        </button>
                    </div>
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
