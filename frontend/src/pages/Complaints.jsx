import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Search, Filter, Plus, MoreVertical,
    Clock, AlertCircle, FileText
} from 'lucide-react';
import { complaintService } from '../services/complaintService';

function Complaints() {
    const [complaints, setComplaints] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, new, in_progress, resolved
    const [search, setSearch] = useState('');

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
                    <h1 className="text-2xl font-bold text-white">Complaints</h1>
                    <p className="text-gray-400 text-sm">Manage and track customer issues</p>
                </div>
                <button
                    onClick={() => navigate('/complaints/new')} // We'll add this route or modal later
                    className="btn-primary flex items-center gap-2"
                >
                    <Plus className="w-4 h-4" />
                    <span>New Complaint</span>
                </button>
            </div>

            {/* Filters & Search */}
            <div className="flex flex-col md:flex-row gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                        type="text"
                        placeholder="Search by subject, customer, or ID..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="input pl-10"
                    />
                </div>
                <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0">
                    {['all', 'new', 'in_progress', 'resolved'].map((s) => (
                        <button
                            key={s}
                            onClick={() => setFilter(s)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${filter === s
                                    ? 'bg-primary-600 text-white'
                                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                                }`}
                        >
                            {s.replace('_', ' ').toUpperCase()}
                        </button>
                    ))}
                </div>
            </div>

            {/* Table */}
            <div className="card overflow-hidden p-0">
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-white/5 border-b border-white/5 text-xs text-gray-400 uppercase tracking-wider">
                                <th className="p-4 font-medium">Subject</th>
                                <th className="p-4 font-medium">Customer</th>
                                <th className="p-4 font-medium">Status</th>
                                <th className="p-4 font-medium">Severity</th>
                                <th className="p-4 font-medium">Assigned To</th>
                                <th className="p-4 font-medium">Date</th>
                                <th className="p-4 font-medium text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {loading ? (
                                <tr>
                                    <td colSpan="7" className="p-8 text-center text-gray-400">
                                        Loading complaints...
                                    </td>
                                </tr>
                            ) : complaints.length === 0 ? (
                                <tr>
                                    <td colSpan="7" className="p-8 text-center text-gray-400">
                                        No complaints found.
                                    </td>
                                </tr>
                            ) : (
                                complaints.map((complaint) => (
                                    <tr
                                        key={complaint.complaint_id}
                                        className="table-row group cursor-pointer"
                                        onClick={() => navigate(`/complaints/${complaint.complaint_id}`)}
                                    >
                                        <td className="p-4">
                                            <div className="flex items-center gap-3">
                                                <div className="p-2 rounded bg-white/5 text-gray-400">
                                                    <FileText className="w-4 h-4" />
                                                </div>
                                                <div>
                                                    <p className="font-medium text-white line-clamp-1">{complaint.subject}</p>
                                                    <p className="text-xs text-gray-500">#{complaint.complaint_id.slice(0, 8)}</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <p className="text-sm text-gray-300">{complaint.customer_name}</p>
                                            <p className="text-xs text-gray-500">{complaint.customer_email}</p>
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
                                                <span className="text-gray-500 text-xs">--</span>
                                            )}
                                        </td>
                                        <td className="p-4">
                                            {complaint.assigned_to_name ? (
                                                <div className="flex items-center gap-2">
                                                    <div className="w-6 h-6 rounded-full bg-primary-500/20 text-primary-400 flex items-center justify-center text-xs font-bold">
                                                        {complaint.assigned_to_name.charAt(0)}
                                                    </div>
                                                    <span className="text-sm text-gray-300">{complaint.assigned_to_name}</span>
                                                </div>
                                            ) : (
                                                <span className="text-sm text-gray-500 italic">Unassigned</span>
                                            )}
                                        </td>
                                        <td className="p-4 text-sm text-gray-400">
                                            {new Date(complaint.created_at).toLocaleDateString()}
                                        </td>
                                        <td className="p-4 text-right">
                                            <button className="p-2 hover:bg-white/10 rounded px-1 transition-colors">
                                                <MoreVertical className="w-4 h-4 text-gray-400" />
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default Complaints;
