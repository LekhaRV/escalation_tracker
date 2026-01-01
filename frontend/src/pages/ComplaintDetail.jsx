import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    ArrowLeft, User, Calendar, Tag, AlertTriangle,
    CheckCircle, Clock, Shield, Send, Lightbulb
} from 'lucide-react';
import { complaintService } from '../services/complaintService';
import { AssignAgentModal } from '../components/common/Modals';
import { useAuth } from '../context/AuthContext';

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

    if (loading) return <div className="text-white">Loading...</div>;
    if (!complaint) return <div className="text-white">Complaint not found</div>;

    return (
        <div className="space-y-6 animate-fade-in relative">
            {/* Header */}
            <div className="flex items-center gap-4">
                <button
                    onClick={() => navigate('/complaints')}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors text-gray-400 hover:text-white"
                >
                    <ArrowLeft className="w-5 h-5" />
                </button>
                <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                        <h1 className="text-xl font-bold text-white">Complaint #{id.slice(0, 8)}</h1>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium uppercase border ${complaint.status === 'new' ? 'border-blue-500/30 text-blue-400 bg-blue-500/10' :
                            complaint.status === 'in_progress' ? 'border-purple-500/30 text-purple-400 bg-purple-500/10' :
                                'border-green-500/30 text-green-400 bg-green-500/10'
                            }`}>
                            {complaint.status.replace('_', ' ')}
                        </span>
                    </div>
                    <p className="text-gray-400 text-sm">Created on {new Date(complaint.created_at).toLocaleString()}</p>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                    <button
                        onClick={() => setShowAssignModal(true)}
                        className="btn-secondary flex items-center gap-2"
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
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Content */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="card">
                        <h2 className="text-lg font-bold text-white mb-4">{complaint.subject}</h2>
                        <div className="p-4 bg-white/5 rounded-lg text-gray-300 whitespace-pre-wrap min-h-[100px]">
                            {complaint.description}
                        </div>

                        {/* Metadata Grid */}
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mt-6 pt-6 border-t border-white/5">
                            <div>
                                <label className="text-xs text-gray-500 font-medium uppercase mb-1 flex items-center gap-1">
                                    <User className="w-3 h-3" /> Customer
                                </label>
                                <p className="text-sm text-white font-medium">{complaint.customer_name}</p>
                                <p className="text-xs text-gray-400">{complaint.customer_email}</p>
                            </div>
                            <div>
                                <label className="text-xs text-gray-500 font-medium uppercase mb-1 flex items-center gap-1">
                                    <Tag className="w-3 h-3" /> Category
                                </label>
                                <p className="text-sm text-white font-medium">
                                    {complaint.category?.category_type || 'Uncategorized'}
                                </p>
                                {complaint.category && (
                                    <div className="flex items-center gap-1 mt-1">
                                        <span className="text-xs text-primary-400 bg-primary-500/10 px-1.5 py-0.5 rounded">
                                            {Math.round(complaint.category.confidence_score * 100)}% AI Confidence
                                        </span>
                                    </div>
                                )}
                            </div>
                            <div>
                                <label className="text-xs text-gray-500 font-medium uppercase mb-1 flex items-center gap-1">
                                    <AlertTriangle className="w-3 h-3" /> Severity
                                </label>
                                <p className={`text-sm font-medium uppercase ${complaint.category?.severity === 'critical' ? 'text-red-400' :
                                    complaint.category?.severity === 'high' ? 'text-orange-400' :
                                        'text-gray-300'
                                    }`}>
                                    {complaint.category?.severity || 'Unknown'}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* AI Recommendations */}
                    <div className="card border-primary-500/20 bg-primary-500/5">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-bold text-primary-400 flex items-center gap-2">
                                <Lightbulb className="w-5 h-5" /> AI Resolution Recommendations
                            </h2>
                            {!recommendations.length && (
                                <button
                                    onClick={generateRecommendations}
                                    disabled={isGenerating}
                                    className="px-3 py-1.5 bg-primary-500/10 hover:bg-primary-500/20 text-primary-400 rounded-lg text-xs font-medium transition-colors border border-primary-500/20 disabled:opacity-50"
                                >
                                    {isGenerating ? "Analyzing..." : "Generate Insights"}
                                </button>
                            )}
                        </div>

                        {recommendations.length > 0 ? (
                            <ul className="space-y-3">
                                {recommendations.map((rec, i) => (
                                    <li key={i} className="flex gap-3 text-gray-300 bg-black/20 p-3 rounded-lg border border-white/5">
                                        <span className="text-primary-400 font-bold bg-primary-500/10 w-6 h-6 flex items-center justify-center rounded-full text-xs shrink-0">
                                            {i + 1}
                                        </span>
                                        <span className="text-sm">{rec}</span>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            !isGenerating && <p className="text-gray-500 text-sm italic">Generate AI insights to see recommended resolution steps based on similar past issues.</p>
                        )}

                        {isGenerating && (
                            <div className="flex items-center gap-2 text-primary-400 text-sm animate-pulse">
                                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                <span>Analyzing complaint details...</span>
                            </div>
                        )}
                    </div>

                    {/* Resolution / Timeline */}
                    <div className="card">
                        <div className="flex gap-6 border-b border-white/5 mb-6">
                            <button
                                onClick={() => setActiveTab('details')}
                                className={`pb-2 text-sm font-medium transition-colors ${activeTab === 'details' ? 'text-primary-400 border-b-2 border-primary-400' : 'text-gray-400 hover:text-white'
                                    }`}
                            >
                                Timeline
                            </button>
                            <button
                                onClick={() => setActiveTab('resolve')}
                                className={`pb-2 text-sm font-medium transition-colors ${activeTab === 'resolve' ? 'text-primary-400 border-b-2 border-primary-400' : 'text-gray-400 hover:text-white'
                                    }`}
                            >
                                Resolution
                            </button>
                        </div>

                        {activeTab === 'details' ? (
                            <div className="space-y-6 pl-2">
                                {complaint.timeline?.map((event, i) => (
                                    <div key={i} className="relative pl-6 pb-2 border-l border-white/10 last:border-0">
                                        <div className="absolute left-0 top-1 -translate-x-1/2 w-3 h-3 bg-gray-700 rounded-full border-2 border-[#1e293b] ring-2 ring-[#0f172a]" />
                                        <div className="flex flex-col">
                                            <span className="text-xs text-gray-500">
                                                {new Date(event.timestamp).toLocaleString()}
                                            </span>
                                            <span className="text-sm text-gray-300">{event.description}</span>
                                            <span className="text-xs font-medium text-primary-500/80 uppercase mt-0.5">{event.type}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div>
                                    <label className="text-sm text-gray-400 block mb-2">Resolution Notes</label>
                                    <textarea
                                        className="input h-32 resize-none"
                                        placeholder="Describe the solution..."
                                        value={notes}
                                        onChange={(e) => setNotes(e.target.value)}
                                    />
                                </div>
                                <button onClick={handleResolve} className="btn-primary w-full">
                                    Mark as Resolved
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                    {/* Assignment Card */}
                    <div className="card">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-bold text-gray-400 uppercase flex items-center gap-2">
                                <Shield className="w-4 h-4" /> Assignment
                            </h3>
                            <button
                                onClick={() => setShowAssignModal(true)}
                                className="px-3 py-1 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-xs font-medium text-white transition-colors flex items-center gap-2"
                            >
                                {complaint.assignment?.assigned_to_user_id ? 'Change Agent' : 'Smart Assign'}
                            </button>
                        </div>

                        {complaint.assignment?.assigned_user_name ? (
                            <div className="bg-white/5 rounded-lg p-3 flex items-center gap-3 mb-4">
                                <div className="w-10 h-10 rounded-full bg-primary-500 text-white flex items-center justify-center font-bold">
                                    {complaint.assignment.assigned_user_name.charAt(0)}
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-white">{complaint.assignment.assigned_user_name}</p>
                                    <p className="text-xs text-gray-400">Assigned Agent</p>
                                </div>
                            </div>
                        ) : (
                            <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-yellow-500 text-sm mb-4">
                                Unassigned
                            </div>
                        )}

                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-500">SLA Deadline</span>
                                <span className="text-white">
                                    {complaint.assignment?.sla_deadline
                                        ? new Date(complaint.assignment.sla_deadline).toLocaleDateString()
                                        : '--'}
                                </span>
                            </div>
                            {complaint.assignment?.assignment_reason && (
                                <div className="pt-2 mt-2 border-t border-white/5">
                                    <p className="text-xs text-gray-500 italic">
                                        "{complaint.assignment.assignment_reason}"
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Project Info */}
                    <div className="card">
                        <h3 className="text-sm font-bold text-gray-400 uppercase mb-4 flex items-center gap-2">
                            <BriefcaseIcon className="w-4 h-4" /> Project
                        </h3>
                        {complaint.project_name ? (
                            <div>
                                <p className="text-lg font-medium text-white mb-1">{complaint.project_name}</p>
                                <p className="text-xs text-primary-400 cursor-pointer hover:underline" onClick={() => navigate(`/projects/${complaint.project_id}`)}>View Project Details</p>
                            </div>
                        ) : (
                            <p className="text-sm text-gray-500 italic">No project linked</p>
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
