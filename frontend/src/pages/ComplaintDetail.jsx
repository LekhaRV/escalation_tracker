import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    ArrowLeft, User, Users, Calendar, Tag, AlertTriangle,
    CheckCircle, Clock, Shield, Send, Lightbulb
} from 'lucide-react';
import { complaintService } from '../services/complaintService';
import { AssignAgentModal } from '../components/common/Modals';
import { useAuth } from '../context/AuthContext';
import CommentsPanel from '../components/dashboard/CommentsPanel';
import SlaCountdown from '../components/common/SlaCountdown';

function ComplaintDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();

    const [complaint, setComplaint] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('details');
    const [notes, setNotes] = useState('');
    const [recommendations, setRecommendations] = useState([]);
    const [isGenerating, setIsGenerating] = useState(false);

    useEffect(() => {
        fetchDetail();
    }, [id]);

    const fetchDetail = async () => {
        try {
            const data = await complaintService.getComplaint(id);
            setComplaint(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleStatusUpdate = async (newStatus) => {
        try {
            await complaintService.updateComplaint(id, { status: newStatus });
            fetchDetail();
        } catch (error) {
            console.error(error);
        }
    };

    const handleResolve = async () => {
        try {
            await complaintService.updateComplaint(id, {
                status: 'resolved',
                resolution_notes: notes
            });
            fetchDetail();
            setNotes('');
        } catch (error) {
            console.error(error);
        }
    };

    const generateRecommendations = async () => {
        setIsGenerating(true);
        try {
            const steps = await complaintService.getResolutionRecommendations(id);
            setRecommendations(steps);
        } catch (error) {
            console.error(error);
        } finally {
            setIsGenerating(false);
        }
    };

    const [showAssignModal, setShowAssignModal] = useState(false);

    const handleAssign = async (userId) => {
        try {
            await complaintService.updateComplaint(id, { assign_to_user_id: userId });
            setShowAssignModal(false);
            fetchDetail();
        } catch (error) {
            console.error("Failed to assign user", error);
        }
    };

    // Helper for Status Badge
    const getStatusBadge = (status) => {
        switch (status) {
            case 'new': return 'border-blue-200 text-blue-700 bg-blue-50';
            case 'in_progress': return 'border-purple-200 text-purple-700 bg-purple-50';
            case 'resolved': return 'border-green-200 text-green-700 bg-green-50';
            default: return 'border-slate-200 text-slate-700 bg-slate-50';
        }
    };

    if (loading) return (
        <div className="flex justify-center items-center h-64 text-slate-600 font-medium">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mr-3"></div>
            Loading complaint details...
        </div>
    );

    if (!complaint) return (
        <div className="text-center p-8 text-slate-900 font-medium">
            Complaint not found or you don't have permission to view it.
        </div>
    );

    return (
        <div className="space-y-6 animate-fade-in relative max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center gap-4">
                <button
                    onClick={() => navigate('/complaints')}
                    className="p-2 hover:bg-slate-100 rounded-lg transition-colors text-slate-500 hover:text-slate-900"
                >
                    <ArrowLeft className="w-5 h-5" />
                </button>
                <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                        <h1 className="text-xl font-bold text-slate-900">Complaint #{id.slice(0, 8)}</h1>
                        <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase border ${getStatusBadge(complaint.status)}`}>
                            {complaint.status.replace('_', ' ')}
                        </span>
                    </div>
                    <p className="text-slate-500 text-sm">Created on {new Date(complaint.created_at).toLocaleString()}</p>
                </div>

                {/* Actions */}
                {user?.role !== 'viewer' && (
                    <div className="flex gap-2">
                        <button
                            onClick={() => setShowAssignModal(true)}
                            className="btn-secondary flex items-center gap-2"
                            title={user?.role === 'agent' ? "Self Assign Only" : "Assign Agent"}
                        >
                            <Shield className="w-4 h-4" />
                            <span>{complaint.assignment?.assigned_to_user_id ? 'Reassign' : 'Assign'}</span>
                        </button>
                        {complaint.status !== 'resolved' && (
                            <button
                                onClick={() => handleStatusUpdate('in_progress')}
                                className="btn-secondary"
                            >
                                In Progress
                            </button>
                        )}
                        <button
                            onClick={() => setActiveTab('resolve')}
                            className="btn-primary"
                        >
                            Resolve
                        </button>
                    </div>
                )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Content */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="card bg-white border border-slate-200 shadow-sm p-6 rounded-xl">
                        <h2 className="text-lg font-bold text-slate-900 mb-4">{complaint.subject}</h2>
                        <div className="p-4 bg-slate-50 border border-slate-100 rounded-lg text-slate-700 whitespace-pre-wrap min-h-[100px]">
                            {complaint.description}
                        </div>

                        {/* Metadata Grid */}
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mt-6 pt-6 border-t border-slate-100">
                            <div>
                                <label className="text-xs text-slate-500 font-semibold uppercase mb-1 flex items-center gap-1">
                                    <User className="w-3 h-3" /> Customer
                                </label>
                                <p className="text-sm text-slate-900 font-medium">{complaint.customer_name}</p>
                                <p className="text-xs text-slate-500">{complaint.customer_email}</p>
                            </div>
                            <div>
                                <label className="text-xs text-slate-500 font-semibold uppercase mb-1 flex items-center gap-1">
                                    <Tag className="w-3 h-3" /> Category
                                </label>
                                <p className="text-sm text-slate-900 font-medium">
                                    {complaint.category?.category_type || 'Uncategorized'}
                                </p>
                                {complaint.category && (
                                    <div className="flex items-center gap-1 mt-1">
                                        <span className="text-xs text-emerald-700 bg-emerald-50 border border-emerald-100 px-1.5 py-0.5 rounded font-medium">
                                            {Math.round(complaint.category.confidence_score * 100)}% AI Confidence
                                        </span>
                                    </div>
                                )}
                            </div>
                            <div>
                                <label className="text-xs text-slate-500 font-semibold uppercase mb-1 flex items-center gap-1">
                                    <AlertTriangle className="w-3 h-3" /> Severity
                                </label>
                                <p className={`text-sm font-bold uppercase ${complaint.category?.severity === 'critical' ? 'text-red-600' :
                                        complaint.category?.severity === 'high' ? 'text-orange-600' :
                                            'text-slate-600'
                                    }`}>
                                    {complaint.category?.severity || 'Unknown'}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Comments Section */}
                    {complaint && (
                        <CommentsPanel
                            complaintId={id}
                            comments={complaint.comments}
                            onCommentAdded={fetchDetail}
                        />
                    )}

                    {/* AI Recommendations */}
                    <div className="card bg-white border border-primary-100 shadow-sm p-6 rounded-xl relative overflow-hidden">
                        <div className="absolute top-0 left-0 w-1 h-full bg-primary-500"></div>
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                                <Lightbulb className="w-5 h-5 text-primary-500" /> AI Resolution Recommendations
                            </h2>
                            {!recommendations.length && (
                                <button
                                    onClick={generateRecommendations}
                                    disabled={isGenerating}
                                    className="px-3 py-1.5 bg-primary-50 hover:bg-primary-100 text-primary-700 border border-primary-200 rounded-lg text-xs font-semibold transition-colors disabled:opacity-50"
                                >
                                    {isGenerating ? "Analyzing..." : "Generate Insights"}
                                </button>
                            )}
                        </div>

                        {recommendations.length > 0 ? (
                            <ul className="space-y-3">
                                {recommendations.map((rec, i) => (
                                    <li key={i} className="flex gap-3 text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-100">
                                        <span className="text-primary-700 font-bold bg-primary-100 w-6 h-6 flex items-center justify-center rounded-full text-xs shrink-0">
                                            {i + 1}
                                        </span>
                                        <span className="text-sm font-medium">{rec}</span>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            !isGenerating && <p className="text-slate-500 text-sm italic">Generate AI insights to see recommended resolution steps based on similar past issues.</p>
                        )}

                        {isGenerating && (
                            <div className="flex items-center gap-2 text-primary-600 text-sm animate-pulse mt-4">
                                <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                <span>Analyzing complaint details...</span>
                            </div>
                        )}
                    </div>

                    {/* Resolution / Timeline */}
                    <div className="card bg-white border border-slate-200 shadow-sm p-6 rounded-xl">
                        <div className="flex gap-6 border-b border-slate-100 mb-6">
                            <button
                                onClick={() => setActiveTab('details')}
                                className={`pb-2 text-sm font-semibold transition-colors ${activeTab === 'details' ? 'text-primary-600 border-b-2 border-primary-500' : 'text-slate-500 hover:text-slate-800'
                                    }`}
                            >
                                Timeline
                            </button>
                            <button
                                onClick={() => setActiveTab('resolve')}
                                className={`pb-2 text-sm font-semibold transition-colors ${activeTab === 'resolve' ? 'text-primary-600 border-b-2 border-primary-500' : 'text-slate-500 hover:text-slate-800'
                                    }`}
                            >
                                Resolution
                            </button>
                        </div>

                        {activeTab === 'details' ? (
                            <div className="space-y-6 pl-2">
                                {complaint.timeline?.map((event, i) => (
                                    <div key={i} className="relative pl-6 pb-2 border-l border-slate-200 last:border-0">
                                        <div className="absolute left-0 top-1 -translate-x-1/2 w-3 h-3 bg-slate-400 rounded-full border-2 border-white ring-2 ring-slate-100" />
                                        <div className="flex flex-col">
                                            <span className="text-xs text-slate-500 font-medium">
                                                {new Date(event.timestamp).toLocaleString()}
                                            </span>
                                            <span className="text-sm text-slate-800 font-medium mt-0.5">{event.description}</span>
                                            <span className="text-xs font-bold text-primary-600 uppercase mt-0.5">{event.type}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div>
                                    <label className="text-sm text-slate-600 font-medium block mb-2">Resolution Notes</label>
                                    <textarea
                                        className="input h-32 resize-none bg-white border-slate-300 text-slate-900 focus:border-primary-500 focus:ring-primary-500"
                                        placeholder="Describe the solution..."
                                        value={notes}
                                        onChange={(e) => setNotes(e.target.value)}
                                    />
                                </div>
                                <button onClick={handleResolve} className="btn-primary w-full shadow-md">
                                    Mark as Resolved
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                    {/* Assignment Card */}
                    <div className="card bg-white border border-slate-200 shadow-sm p-6 rounded-xl">
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex items-center gap-2 text-slate-600 mb-1">
                                <Users className="w-4 h-4" />
                                <h3 className="text-xs font-bold uppercase tracking-wider">Assignment</h3>
                            </div>
                            {['admin', 'manager'].includes(user?.role?.toLowerCase()) && (
                                <button
                                    onClick={() => setShowAssignModal(true)}
                                    className="text-xs text-primary-600 hover:text-primary-700 border border-primary-200 hover:bg-primary-50 px-2 py-1 rounded transition-colors font-medium"
                                >
                                    Change Agent
                                </button>
                            )}
                        </div>

                        {complaint.assignment?.assigned_user_name ? (
                            <div className="bg-slate-50 border border-slate-100 rounded-lg p-3 flex items-center gap-3 mb-4">
                                <div className="w-10 h-10 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-bold shadow-sm">
                                    {complaint.assignment.assigned_user_name.charAt(0)}
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-slate-900">{complaint.assignment.assigned_user_name}</p>
                                    <p className="text-xs text-slate-500">Assigned Agent</p>
                                </div>
                            </div>
                        ) : (
                            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-700 text-sm font-medium mb-4 flex items-center gap-2">
                                <AlertTriangle className="w-4 h-4" /> Unassigned
                            </div>
                        )}

                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-slate-500 flex items-center gap-2 font-medium">
                                    SLA Deadline
                                    <SlaCountdown deadline={complaint.assignment?.sla_deadline} />
                                </span>
                                <span className="text-slate-900 font-bold">
                                    {complaint.assignment?.sla_deadline
                                        ? new Date(complaint.assignment.sla_deadline).toLocaleDateString()
                                        : '--'}
                                </span>
                            </div>
                            {complaint.assignment?.assignment_reason && (
                                <div className="pt-2 mt-2 border-t border-slate-100">
                                    <p className="text-xs text-slate-500 italic bg-slate-50 p-2 rounded">
                                        "{complaint.assignment.assignment_reason}"
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Project Info */}
                    <div className="card bg-white border border-slate-200 shadow-sm p-6 rounded-xl">
                        <h3 className="text-xs font-bold text-slate-500 uppercase mb-4 flex items-center gap-2">
                            <BriefcaseIcon className="w-4 h-4" /> Project
                        </h3>
                        {complaint.project_name ? (
                            <div>
                                <p className="text-lg font-bold text-slate-900 mb-1">{complaint.project_name}</p>
                                <p className="text-xs text-primary-600 font-semibold cursor-pointer hover:underline flex items-center gap-1" onClick={() => navigate(`/projects/${complaint.project_id}`)}>
                                    View Project Details <ArrowLeft className="w-3 h-3 rotate-180" />
                                </p>
                            </div>
                        ) : (
                            <p className="text-sm text-slate-500 italic">No project linked</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Assignment Modal */}
            <AssignAgentModal
                isOpen={showAssignModal}
                onClose={() => setShowAssignModal(false)}
                onAssign={handleAssign}
                currentAssignee={complaint.assignment?.assigned_to_user_id}
                complaintId={id}
            />
        </div>
    );
}

// Temporary icon
const BriefcaseIcon = (props) => (
    <svg
        {...props}
        xmlns="http://www.w3.org/2000/svg"
        width="24" height="24" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
    >
        <rect width="20" height="14" x="2" y="7" rx="2" ry="2" />
        <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
    </svg>
)

export default ComplaintDetail;
