import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
    Search, Filter, Plus, MoreVertical,
    Clock, AlertCircle, FileText, Mail, X, Zap,
    Inbox, CheckCircle, Activity
} from 'lucide-react';
import { complaintService } from '../services/complaintService';
import { CreateComplaintModal, SimulateEmailModal, AssignAgentModal } from '../components/common/Modals';
import SlaCountdown from '../components/common/SlaCountdown';

function Complaints() {
    const { user } = useAuth();
    const [complaints, setComplaints] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, new, in_progress, resolved
    const [search, setSearch] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);
    const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
    const [selectedComplaint, setSelectedComplaint] = useState(null);
    const [actionMenuOpen, setActionMenuOpen] = useState(null); // complaint_id

    const [page, setPage] = useState(1);
    const [pageSize] = useState(8);
    const [totalPages, setTotalPages] = useState(1);
    const [totalItems, setTotalItems] = useState(0);

    const navigate = useNavigate();
    const [searchParams, setSearchParams] = useSearchParams();
    const projectIdFilter = searchParams.get('project_id');
    const severityFilter = searchParams.get('severity');
    const statusFromUrl = searchParams.get('status');
    const overdueFilter = searchParams.get('overdue');
    const idsFilter = searchParams.get('ids');

    // Use URL status if provided, otherwise use local filter
    const effectiveStatus = statusFromUrl || (filter !== 'all' ? filter : undefined);

    useEffect(() => {
        setPage(1); // Reset page on filter change
    }, [filter, search, projectIdFilter, severityFilter, statusFromUrl, overdueFilter]);

    useEffect(() => {
        fetchComplaints();
    }, [page, filter, search, projectIdFilter, severityFilter, statusFromUrl, overdueFilter]);

    const fetchComplaints = async () => {
        setLoading(true);
        try {
            const params = {
                status: effectiveStatus,
                severity: severityFilter || undefined,
                search: search || undefined,
                project_id: projectIdFilter || undefined,
                overdue: overdueFilter === 'true' ? true : undefined,
                ids: idsFilter || undefined,
                page: page,
                page_size: pageSize
            };
            const data = await complaintService.getComplaints(params);
            setComplaints(data.items);
            setTotalPages(data.total_pages);
            setTotalItems(data.total);
        } catch (error) {
            console.error('Failed to fetch complaints', error);
        } finally {
            setLoading(false);
        }
    };

    const clearAllFilters = () => {
        setSearchParams({});
        setFilter('all');
    };

    const hasUrlFilters = projectIdFilter || severityFilter || statusFromUrl || overdueFilter;

    const handleCreateComplaint = async (data) => {
        try {
            await complaintService.createComplaint(data);
            setIsModalOpen(false);
            fetchComplaints();
        } catch (error) {
            console.error(error);
            alert('Failed to create complaint');
        }
    };

    const handleSimulateEmail = async (data) => {
        try {
            await complaintService.simulateEmail(data);
            setIsEmailModalOpen(false);

            // Wait a moment for AI processing to finish
            setLoading(true);
            setTimeout(() => {
                fetchComplaints();
            }, 2000);
        } catch (error) {
            console.error(error);
            alert('Failed to simulate email');
        }
    };

    const handleAssign = async (userId) => {
        try {
            await complaintService.assignAgent(selectedComplaint.complaint_id, userId);
            setIsAssignModalOpen(false);
            setSelectedComplaint(null);
            fetchComplaints();
        } catch (error) {
            console.error(error);
            alert('Failed to assign agent');
        }
    };

    const openAssignModal = (e, complaint) => {
        e.stopPropagation();
        setSelectedComplaint(complaint);
        setIsAssignModalOpen(true);
        setActionMenuOpen(null);
    };

    const getSeverityBadge = (severity) => {
        const maps = {
            critical: 'badge-critical',
            high: 'badge-high',
            medium: 'badge-medium',
            low: 'badge-lowest'
        };
        return maps[severity] || 'badge-lowest';
    };

    const getStatusBadge = (status) => {
        return `status-${status}`;
    };

    // Calculate quick stats
    const newCount = complaints.filter(c => c.status?.toLowerCase() === 'new').length;
    const inProgressCount = complaints.filter(c => c.status?.toLowerCase() === 'in_progress').length;
    const resolvedCount = complaints.filter(c => c.status?.toLowerCase() === 'resolved').length;

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/25">
                        <FileText className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-slate-800">Complaints</h1>
                        <p className="text-slate-500 text-sm">Manage and track customer issues</p>
                    </div>
                </div>
                {hasUrlFilters && (
                    <div className="mt-2 flex items-center gap-2 flex-wrap">
                        {severityFilter && (
                            <span className="px-3 py-1 bg-red-50 text-red-700 border border-red-200 rounded-full text-xs font-bold uppercase">
                                {severityFilter.charAt(0).toUpperCase() + severityFilter.slice(1)} Severity
                            </span>
                        )}
                        {overdueFilter && (
                            <span className="px-3 py-1 bg-amber-50 text-amber-700 border border-amber-100 rounded-full text-xs font-bold uppercase">
                                Overdue (Past SLA)
                            </span>
                        )}
                        {statusFromUrl && (
                            <span className="px-3 py-1 bg-purple-50 text-purple-700 border border-purple-200 rounded-full text-xs font-bold uppercase">
                                {statusFromUrl.replace('_', ' ')}
                            </span>
                        )}
                        {projectIdFilter && (
                            <span className="px-3 py-1 bg-primary-50 text-primary-700 border border-primary-200 rounded-full text-xs font-bold uppercase">
                                Filtered by Project
                            </span>
                        )}
                        {idsFilter && (
                            <span className="px-3 py-1 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-full text-xs font-bold uppercase flex items-center gap-1">
                                <Zap className="w-3 h-3" />
                                Pattern Match
                            </span>
                        )}
                        <button
                            onClick={clearAllFilters}
                            className="px-2 py-1 text-muted hover:text-logic hover:bg-slate-100 rounded text-sm flex items-center gap-1 transition-colors"
                        >
                            <X className="w-3 h-3" />
                            Clear filters
                        </button>
                    </div>
                )}
                <div className="flex gap-3 ml-auto">
                    {['admin', 'manager'].includes(user?.role?.toLowerCase()) && (
                        <button
                            onClick={() => setIsEmailModalOpen(true)}
                            className="btn-secondary flex items-center gap-2"
                            title="Debug Tool: Inject fake email"
                        >
                            <Mail className="w-4 h-4" />
                            <span className="hidden md:inline">Simulate Email</span>
                        </button>
                    )}
                    {['admin', 'manager', 'agent'].includes(user?.role?.toLowerCase()) && (
                        <button
                            onClick={() => setIsModalOpen(true)}
                            className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl font-semibold shadow-lg shadow-blue-500/25 hover:shadow-xl transition-all"
                        >
                            <Plus className="w-4 h-4" />
                            <span>New Complaint</span>
                        </button>
                    )}
                </div>
            </div>

            {/* Filters & Search */}
            <div className="flex flex-col md:flex-row gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input
                        type="text"
                        placeholder="Search by subject, customer, or ID..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="input pl-14"
                    />
                </div>
                <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0">
                    <button
                        onClick={() => setFilter('all')}
                        className={`px-4 py-2 rounded-xl text-sm font-semibold whitespace-nowrap transition-all ${filter === 'all'
                            ? 'bg-slate-800 text-white shadow-lg'
                            : 'bg-white text-slate-600 border border-slate-200 hover:border-slate-300'
                            }`}
                    >
                        All
                    </button>
                    <button
                        onClick={() => setFilter('new')}
                        className={`px-4 py-2 rounded-xl text-sm font-semibold whitespace-nowrap transition-all flex items-center gap-2 ${filter === 'new'
                            ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/25'
                            : 'bg-blue-50 text-blue-600 border border-blue-200 hover:bg-blue-100'
                            }`}
                    >
                        <Inbox className="w-4 h-4" /> New
                    </button>
                    <button
                        onClick={() => setFilter('in_progress')}
                        className={`px-4 py-2 rounded-xl text-sm font-semibold whitespace-nowrap transition-all flex items-center gap-2 ${filter === 'in_progress'
                            ? 'bg-violet-500 text-white shadow-lg shadow-violet-500/25'
                            : 'bg-violet-50 text-violet-600 border border-violet-200 hover:bg-violet-100'
                            }`}
                    >
                        <Activity className="w-4 h-4" /> In Progress
                    </button>
                    <button
                        onClick={() => setFilter('resolved')}
                        className={`px-4 py-2 rounded-xl text-sm font-semibold whitespace-nowrap transition-all flex items-center gap-2 ${filter === 'resolved'
                            ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/25'
                            : 'bg-emerald-50 text-emerald-600 border border-emerald-200 hover:bg-emerald-100'
                            }`}
                    >
                        <CheckCircle className="w-4 h-4" /> Resolved
                    </button>
                </div>
            </div>

            {/* Table */}
            <div className="card bg-surface border border-slate-200 shadow-sm rounded-xl overflow-hidden p-0">
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-app border-b border-slate-200 text-xs text-muted font-bold uppercase tracking-wider">
                                <th className="p-4 font-bold">Subject</th>
                                <th className="p-4 font-bold">Customer</th>
                                <th className="p-4 font-bold">Status</th>
                                <th className="p-4 font-bold">Severity</th>
                                <th className="p-4 font-bold">Assigned To</th>
                                <th className="p-4 font-bold">Date</th>
                                <th className="p-4 font-bold text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {loading ? (
                                <tr>
                                    <td colSpan="7" className="p-12 text-center text-slate-500">
                                        Loading complaints...
                                    </td>
                                </tr>
                            ) : complaints.length === 0 ? (
                                <tr>
                                    <td colSpan="7" className="p-12 text-center text-slate-500">
                                        No complaints found.
                                    </td>
                                </tr>
                            ) : (
                                complaints.map((complaint) => (
                                    <tr
                                        key={complaint.complaint_id}
                                        className="table-row group cursor-pointer hover:bg-brand-50/50 transition-colors"
                                        onClick={() => navigate(`/complaints/${complaint.complaint_id}`)}
                                    >
                                        <td className="p-4">
                                            <div className="flex items-center gap-3">
                                                <div className="p-2 rounded bg-brand-50 text-brand-600 border border-brand-100">
                                                    <FileText className="w-4 h-4" />
                                                </div>
                                                <div>
                                                    <p className="font-bold text-logic line-clamp-1">{complaint.subject}</p>
                                                    <p className="text-xs text-muted font-mono">#{complaint.complaint_id.slice(0, 8)}</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <p className="text-sm font-medium text-algo">{complaint.customer_name}</p>
                                            <p className="text-xs text-muted">{complaint.customer_email}</p>
                                        </td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${getStatusBadge(complaint.status)}`}>
                                                {complaint.status.replace('_', ' ')}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            {complaint.severity ? (
                                                <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${getSeverityBadge(complaint.severity)}`}>
                                                    {complaint.severity}
                                                </span>
                                            ) : (
                                                <span className="text-slate-400 text-xs">--</span>
                                            )}
                                        </td>
                                        <td className="p-4">
                                            {complaint.assigned_to_name ? (
                                                <div className="flex items-center gap-2">
                                                    <div className="w-6 h-6 rounded-full bg-brand-50 text-brand-600 flex items-center justify-center text-xs font-bold border border-brand-100">
                                                        {complaint.assigned_to_name.charAt(0)}
                                                    </div>
                                                    <span className="text-sm font-medium text-algo">{complaint.assigned_to_name}</span>
                                                </div>
                                            ) : (
                                                <span className="text-sm text-slate-400 italic font-medium flex items-center gap-1">
                                                    <AlertCircle className="w-3 h-3" /> Unassigned
                                                </span>
                                            )}
                                        </td>
                                        <td className="p-4 text-sm text-algo">
                                            <div className="flex flex-col gap-1">
                                                <span className="font-medium">{new Date(complaint.created_at).toLocaleDateString()}</span>
                                                <SlaCountdown deadline={complaint.sla_deadline} status={complaint.status} size="sm" showIcon={false} />
                                            </div>
                                        </td>
                                        <td className="p-4 text-right">
                                            <div className="relative flex items-center gap-2 justify-end">
                                                {!complaint.assigned_to_name && ['admin', 'manager'].includes(user?.role?.toLowerCase()) && (
                                                    <button
                                                        onClick={(e) => openAssignModal(e, complaint)}
                                                        className="px-2 py-1 bg-primary-50 text-primary-700 border border-primary-200 hover:bg-primary-100 text-xs font-bold rounded transition-colors"
                                                    >
                                                        Smart Assign
                                                    </button>
                                                )}
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setActionMenuOpen(actionMenuOpen === complaint.complaint_id ? null : complaint.complaint_id);
                                                    }}
                                                    className="p-2 hover:bg-brand-50 rounded px-1 transition-colors text-muted hover:text-logic"
                                                >
                                                    <MoreVertical className="w-4 h-4" />
                                                </button>

                                                {actionMenuOpen === complaint.complaint_id && (
                                                    <div className="absolute right-0 top-full mt-1 w-48 rounded-lg shadow-xl bg-surface border border-slate-200 z-50 animate-fade-in-up">
                                                        <div className="py-1" role="menu">
                                                            {['admin', 'manager'].includes(user?.role?.toLowerCase()) && (
                                                                <button
                                                                    onClick={(e) => openAssignModal(e, complaint)}
                                                                    className="block px-4 py-2 text-sm text-logic font-medium hover:bg-brand-50 w-full text-left"
                                                                >
                                                                    {complaint.assigned_to_name ? 'Reassign Agent' : 'Smart Assign Agent'}
                                                                </button>
                                                            )}
                                                            <button
                                                                onClick={(e) => { e.stopPropagation(); navigate(`/complaints/${complaint.complaint_id}`) }}
                                                                className="block px-4 py-2 text-sm text-logic font-medium hover:bg-brand-50 w-full text-left"
                                                            >
                                                                View Details
                                                            </button>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between border-t border-slate-200 pt-4">
                <p className="text-sm text-muted">
                    Showing <span className="font-medium">{(page - 1) * pageSize + 1}</span> to <span className="font-medium">{Math.min(page * pageSize, totalItems)}</span> of <span className="font-medium">{totalItems}</span> results
                </p>
                <div className="flex gap-2">
                    <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="px-3 py-1 text-sm font-medium text-algo bg-surface border border-slate-200 rounded-lg hover:bg-brand-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        Previous
                    </button>
                    <button
                        onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
                        className="px-3 py-1 text-sm font-medium text-algo bg-surface border border-slate-200 rounded-lg hover:bg-brand-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        Next
                    </button>
                </div>
            </div>

            <CreateComplaintModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onCreate={handleCreateComplaint}
            />

            <SimulateEmailModal
                isOpen={isEmailModalOpen}
                onClose={() => setIsEmailModalOpen(false)}
                onSend={handleSimulateEmail}
            />

            <AssignAgentModal
                isOpen={isAssignModalOpen}
                onClose={() => setIsAssignModalOpen(false)}
                onAssign={handleAssign}
                currentAssignee={selectedComplaint?.assigned_to_user_id}
                complaintId={selectedComplaint?.complaint_id}
            />
        </div >
    );
}

export default Complaints;
