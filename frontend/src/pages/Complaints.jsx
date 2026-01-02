import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Search, Filter, Plus, MoreVertical,
    Clock, AlertCircle, FileText, Mail
} from 'lucide-react';
import { complaintService } from '../services/complaintService';
import { CreateComplaintModal, SimulateEmailModal, AssignAgentModal } from '../components/common/Modals';

function Complaints() {
    const [complaints, setComplaints] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, new, in_progress, resolved
    const [search, setSearch] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);
    const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
    const [selectedComplaint, setSelectedComplaint] = useState(null);
    const [actionMenuOpen, setActionMenuOpen] = useState(null); // complaint_id

    const navigate = useNavigate();

    useEffect(() => {
        fetchComplaints();
    }, [filter, search]);

    const fetchComplaints = async () => {
        setLoading(true);
        try {
            const params = {
                status: filter !== 'all' ? filter : undefined,
                search: search || undefined
            };
            const data = await complaintService.getComplaints(params);
            setComplaints(data.items);
        } catch (error) {
            console.error('Failed to fetch complaints', error);
        } finally {
            setLoading(false);
        }
    };

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
            low: 'badge-low'
        };
        return maps[severity] || 'badge-low';
    };

    const getStatusBadge = (status) => {
        return `status-${status}`;
    };

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Escalations</h1>
                    <p className="text-slate-500 text-sm">Manage and track customer issues</p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={() => setIsEmailModalOpen(true)}
                        className="btn-secondary flex items-center gap-2"
                        title="Debug Tool: Inject fake email"
                    >
                        <Mail className="w-4 h-4" />
                        <span className="hidden md:inline">Simulate Email</span>
                    </button>
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="btn-primary flex items-center gap-2"
                    >
                        <Plus className="w-4 h-4" />
                        <span>New Complaint</span>
                    </button>
                </div>
            </div>

            {/* Filters & Search */}
            <div className="flex flex-col md:flex-row gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <input
                        type="text"
                        placeholder="Search by subject, customer, or ID..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="input pl-14 bg-white border-slate-200 text-slate-900 focus:border-blue-500"
                    />
                </div>
                <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0">
                    {['all', 'new', 'in_progress', 'resolved'].map((s) => (
                        <button
                            key={s}
                            onClick={() => setFilter(s)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${filter === s
                                ? 'bg-blue-600 text-white'
                                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                                }`}
                        >
                            {s.replace('_', ' ').toUpperCase()}
                        </button>
                    ))}
                </div>
            </div>

            {/* Table */}
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden p-0">
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-slate-50 border-b border-slate-200 text-xs text-slate-500 uppercase tracking-wider">
                                <th className="p-4 font-medium">Subject</th>
                                <th className="p-4 font-medium">Customer</th>
                                <th className="p-4 font-medium">Status</th>
                                <th className="p-4 font-medium">Severity</th>
                                <th className="p-4 font-medium">Assigned To</th>
                                <th className="p-4 font-medium">Date</th>
                                <th className="p-4 font-medium text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {loading ? (
                                <tr>
                                    <td colSpan="7" className="p-8 text-center text-slate-500">
                                        Loading complaints...
                                    </td>
                                </tr>
                            ) : complaints.length === 0 ? (
                                <tr>
                                    <td colSpan="7" className="p-8 text-center text-slate-500">
                                        No complaints found.
                                    </td>
                                </tr>
                            ) : (
                                complaints.map((complaint) => (
                                    <tr
                                        key={complaint.complaint_id}
                                        className="table-row group cursor-pointer hover:bg-slate-50"
                                        onClick={() => navigate(`/complaints/${complaint.complaint_id}`)}
                                    >
                                        <td className="p-4">
                                            <div className="flex items-center gap-3">
                                                <div className="p-2 rounded bg-slate-100 text-slate-500">
                                                    <FileText className="w-4 h-4" />
                                                </div>
                                                <div>
                                                    <p className="font-medium text-slate-900 line-clamp-1">{complaint.subject}</p>
                                                    <p className="text-xs text-slate-500">#{complaint.complaint_id.slice(0, 8)}</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <p className="text-sm text-slate-700">{complaint.customer_name}</p>
                                            <p className="text-xs text-slate-500">{complaint.customer_email}</p>
                                        </td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 rounded text-xs font-medium uppercase ${getStatusBadge(complaint.status)}`}>
                                                {complaint.status.replace('_', ' ')}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            {complaint.severity ? (
                                                <span className={`px-2 py-1 rounded text-xs font-medium uppercase ${getSeverityBadge(complaint.severity)}`}>
                                                    {complaint.severity}
                                                </span>
                                            ) : (
                                                <span className="text-slate-400 text-xs">--</span>
                                            )}
                                        </td>
                                        <td className="p-4">
                                            {complaint.assigned_to_name ? (
                                                <div className="flex items-center gap-2">
                                                    <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold">
                                                        {complaint.assigned_to_name.charAt(0)}
                                                    </div>
                                                    <span className="text-sm text-slate-600">{complaint.assigned_to_name}</span>
                                                </div>
                                            ) : (
                                                <span className="text-sm text-slate-400 italic">Unassigned</span>
                                            )}
                                        </td>
                                        <td className="p-4 text-sm text-slate-500">
                                            {new Date(complaint.created_at).toLocaleDateString()}
                                        </td>
                                        <td className="p-4 text-right">
                                            <div className="relative flex items-center gap-2 justify-end">
                                                {!complaint.assigned_to_name && complaint.status !== 'resolved' && (
                                                    <button
                                                        onClick={(e) => openAssignModal(e, complaint)}
                                                        className="px-2 py-1 bg-blue-50 hover:bg-blue-100 text-blue-600 text-xs font-medium rounded transition-colors"
                                                    >
                                                        Smart Assign
                                                    </button>
                                                )}
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setActionMenuOpen(actionMenuOpen === complaint.complaint_id ? null : complaint.complaint_id);
                                                    }}
                                                    className="p-2 hover:bg-slate-100 rounded px-1 transition-colors"
                                                >
                                                    <MoreVertical className="w-4 h-4 text-slate-400" />
                                                </button>
                                                {actionMenuOpen === complaint.complaint_id && (
                                                    <div className="absolute right-0 top-full mt-1 w-48 rounded-lg shadow-xl bg-white border border-slate-200 z-50 animate-in fade-in zoom-in-95 duration-200">
                                                        <div className="py-1" role="menu">
                                                            {complaint.status !== 'resolved' && (
                                                                <button
                                                                    onClick={(e) => openAssignModal(e, complaint)}
                                                                    className="block px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 w-full text-left transition-colors"
                                                                >
                                                                    {complaint.assigned_to_name ? 'Reassign Agent' : 'Smart Assign Agent'}
                                                                </button>
                                                            )}
                                                            <button
                                                                onClick={(e) => { e.stopPropagation(); navigate(`/complaints/${complaint.complaint_id}`) }}
                                                                className="block px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 w-full text-left transition-colors"
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
        </div>
    );
}

export default Complaints;
