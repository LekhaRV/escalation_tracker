import { useState, useEffect } from 'react';
import { Building2, Users, Loader2, AlertCircle, Briefcase, TrendingUp, UserCheck } from 'lucide-react';
import api from '../services/api';

export default function Departments() {
    const [departments, setDepartments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchDepartments();
    }, []);

    const fetchDepartments = async () => {
        try {
            setLoading(true);
            const response = await api.get('/departments');
            setDepartments(response.data);
        } catch (err) {
            setError('Failed to load departments');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    // Calculate stats
    const totalUsers = departments.reduce((sum, d) => sum + (d.user_count || 0), 0);
    const totalProjects = departments.reduce((sum, d) => sum + (d.project_count || 0), 0);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 text-teal-500 animate-spin" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-64 text-red-500 font-medium">
                <AlertCircle className="w-6 h-6 mr-2" />
                {error}
            </div>
        );
    }

    // Color palette for department cards
    const deptColors = {
        'Engineering': { gradient: 'from-blue-500 to-indigo-600', bg: 'bg-blue-100', text: 'text-blue-600' },
        'Delivery': { gradient: 'from-emerald-500 to-teal-600', bg: 'bg-emerald-100', text: 'text-emerald-600' },
        'DevOps': { gradient: 'from-amber-500 to-orange-600', bg: 'bg-amber-100', text: 'text-amber-600' },
        'QA': { gradient: 'from-purple-500 to-violet-600', bg: 'bg-purple-100', text: 'text-purple-600' },
        'Design': { gradient: 'from-pink-500 to-rose-600', bg: 'bg-pink-100', text: 'text-pink-600' },
        'Client Success': { gradient: 'from-cyan-500 to-blue-600', bg: 'bg-cyan-100', text: 'text-cyan-600' },
        'Data': { gradient: 'from-indigo-500 to-blue-600', bg: 'bg-indigo-100', text: 'text-indigo-600' },
        'HR': { gradient: 'from-rose-500 to-pink-600', bg: 'bg-rose-100', text: 'text-rose-600' },
        'Finance': { gradient: 'from-green-500 to-emerald-600', bg: 'bg-green-100', text: 'text-green-600' },
    };

    const defaultColor = { gradient: 'from-slate-500 to-slate-600', bg: 'bg-slate-100', text: 'text-slate-600' };

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-teal-500/25">
                        <Building2 className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-slate-800">Departments</h1>
                        <p className="text-slate-500 text-sm">Organization structure and team distribution</p>
                    </div>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-4 gap-4">
                <div className="bg-white rounded-xl border border-slate-200 p-5 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-teal-100 flex items-center justify-center">
                        <Building2 className="w-6 h-6 text-teal-600" />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-slate-800">{departments.length}</p>
                        <p className="text-sm text-slate-500">Departments</p>
                    </div>
                </div>
                <div className="bg-white rounded-xl border border-slate-200 p-5 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
                        <Users className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-slate-800">{totalUsers}</p>
                        <p className="text-sm text-slate-500">Total Members</p>
                    </div>
                </div>
                <div className="bg-white rounded-xl border border-slate-200 p-5 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-violet-100 flex items-center justify-center">
                        <Briefcase className="w-6 h-6 text-violet-600" />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-slate-800">{totalProjects}</p>
                        <p className="text-sm text-slate-500">Total Projects</p>
                    </div>
                </div>
                <div className="bg-white rounded-xl border border-slate-200 p-5 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center">
                        <TrendingUp className="w-6 h-6 text-emerald-600" />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-slate-800">
                            {totalUsers > 0 ? Math.round(totalProjects / departments.length) : 0}
                        </p>
                        <p className="text-sm text-slate-500">Avg Projects/Dept</p>
                    </div>
                </div>
            </div>

            {/* Department Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {departments.map((dept) => {
                    const color = deptColors[dept.name] || defaultColor;
                    return (
                        <div
                            key={dept.department_id}
                            className="bg-white border border-slate-200 rounded-2xl overflow-hidden hover:shadow-xl hover:border-slate-300 transition-all group"
                        >
                            {/* Colored Header Bar */}
                            <div className={`h-2 bg-gradient-to-r ${color.gradient}`} />

                            <div className="p-6">
                                <div className="flex items-start justify-between mb-4">
                                    <div className={`p-3 rounded-xl ${color.bg} ${color.text} group-hover:scale-110 transition-transform`}>
                                        <Building2 className="w-6 h-6" />
                                    </div>
                                    {dept.user_count !== undefined && (
                                        <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 rounded-full">
                                            <Users className="w-4 h-4 text-slate-500" />
                                            <span className="text-sm font-bold text-slate-700">{dept.user_count}</span>
                                        </div>
                                    )}
                                </div>

                                <h3 className={`text-lg font-bold text-slate-800 mb-2 group-hover:${color.text} transition-colors`}>
                                    {dept.name}
                                </h3>

                                {dept.description && (
                                    <p className="text-slate-500 text-sm mb-4 line-clamp-2">
                                        {dept.description}
                                    </p>
                                )}

                                {dept.project_count !== undefined && (
                                    <div className="pt-4 border-t border-slate-100">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-2">
                                                <Briefcase className="w-4 h-4 text-slate-400" />
                                                <span className="text-sm text-slate-500">Projects</span>
                                            </div>
                                            <span className="text-lg font-bold text-slate-800">{dept.project_count}</span>
                                        </div>
                                        {/* Project capacity bar */}
                                        <div className="mt-2 h-2 bg-slate-100 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full bg-gradient-to-r ${color.gradient}`}
                                                style={{ width: `${Math.min((dept.project_count / 10) * 100, 100)}%` }}
                                            />
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
