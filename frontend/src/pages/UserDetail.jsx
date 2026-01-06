import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/common/Layout';
import { userService } from '../services/userService';
import { complaintService } from '../services/complaintService';
import { ArrowLeft, Mail, Building, Shield, User as UserIcon, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { CreateUserModal } from '../components/common/Modals';

export default function UserDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [complaints, setComplaints] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showEditModal, setShowEditModal] = useState(false);

    useEffect(() => {
        fetchData();
    }, [id]);

    async function fetchData() {
        try {
            setLoading(true);
            const [userData, complaintsData] = await Promise.all([
                userService.getUser(id),
                complaintService.getComplaints({ assigned_to: id })
            ]);
            setUser(userData);
            setComplaints(complaintsData.items || []);
        } catch (err) {
            console.error(err);
            setError("Failed to load user details");
        } finally {
            setLoading(false);
        }
    }

    if (loading) return (
        <div className="flex items-center justify-center h-64 text-slate-600 font-medium">Loading User Details...</div>
    );

    if (error || !user) return (
        <div className="p-8 text-red-600 bg-red-50 border border-red-200 rounded-lg mx-auto max-w-2xl mt-8 text-center">{error || "User not found"}</div>
    );

    return (
        <div className="space-y-6 max-w-7xl mx-auto animate-fade-in">
            {/* Header */}
            <div className="flex items-center gap-4">
                <button onClick={() => navigate('/users')} className="p-2 hover:bg-slate-100 rounded-lg transition-colors text-slate-500 hover:text-slate-900">
                    <ArrowLeft className="w-6 h-6" />
                </button>
                <h1 className="text-2xl font-bold text-slate-900">User Details</h1>
            </div>

            {/* Profile Card */}
            <div className="card bg-white border border-slate-200 rounded-xl p-8 shadow-sm">
                <div className="flex flex-col md:flex-row gap-8 items-start">
                    {/* Avatar */}
                    <div className="w-24 h-24 rounded-full bg-primary-50 text-primary-600 flex items-center justify-center font-bold text-4xl shrink-0 border border-primary-100 shadow-sm">
                        {user.name.charAt(0).toUpperCase()}
                    </div>

                    {/* Info */}
                    <div className="flex-1 space-y-4 w-full">
                        <div className="flex items-start justify-between w-full">
                            <div>
                                <h2 className="text-2xl font-bold text-slate-900 mb-1">{user.name}</h2>
                                <div className="flex items-center gap-2 text-slate-500 font-medium">
                                    <Mail className="w-4 h-4" />
                                    <span>{user.email}</span>
                                </div>
                            </div>
                            <button
                                onClick={() => setShowEditModal(true)}
                                className="px-4 py-2 bg-white hover:bg-slate-50 text-slate-700 rounded-lg transition-colors border border-slate-200 shadow-sm font-medium text-sm"
                            >
                                Edit Profile
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6 border-t border-slate-100">
                            <div className="flex items-center gap-3 p-4 bg-slate-50 border border-slate-100 rounded-lg">
                                <div className="p-2 bg-purple-100 rounded-lg">
                                    <Shield className="w-5 h-5 text-purple-600" />
                                </div>
                                <div>
                                    <div className="text-xs text-slate-500 uppercase font-bold">Role</div>
                                    <div className="text-sm font-bold text-slate-900 capitalize">{user.role}</div>
                                </div>
                            </div>
                            <div className="flex items-center gap-3 p-4 bg-slate-50 border border-slate-100 rounded-lg">
                                <div className="p-2 bg-blue-100 rounded-lg">
                                    <Building className="w-5 h-5 text-blue-600" />
                                </div>
                                <div>
                                    <div className="text-xs text-slate-500 uppercase font-bold">Department</div>
                                    <div className="text-sm font-bold text-slate-900">{user.department_name || "N/A"}</div>
                                </div>
                            </div>
                            <div className="flex items-center gap-3 p-4 bg-slate-50 border border-slate-100 rounded-lg">
                                <div className={`p-2 rounded-lg ${user.status === 'active' ? 'bg-emerald-100' : 'bg-slate-200'}`}>
                                    <UserIcon className={`w-5 h-5 ${user.status === 'active' ? 'text-emerald-600' : 'text-slate-500'}`} />
                                </div>
                                <div>
                                    <div className="text-xs text-slate-500 uppercase font-bold">Status</div>
                                    <div className="text-sm font-bold text-slate-900 capitalize">{user.status}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Assigned Complaints */}
            <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                <div className="p-6 border-b border-slate-200 flex items-center justify-between bg-slate-50">
                    <h3 className="font-bold text-lg text-slate-900">Assigned Escalations</h3>
                    <span className="px-2.5 py-1 bg-white border border-slate-200 rounded-full text-xs font-bold text-slate-600 shadow-sm">{complaints.length} Total</span>
                </div>

                {complaints.length === 0 ? (
                    <div className="p-12 text-center text-slate-500 flex flex-col items-center gap-2">
                        <CheckCircle className="w-8 h-8 text-emerald-400 opacity-50" />
                        <p>No complaints currently assigned.</p>
                    </div>
                ) : (
                    <div className="divide-y divide-slate-100">
                        {complaints.map(c => (
                            <div
                                key={c.complaint_id}
                                className="p-4 hover:bg-slate-50 cursor-pointer transition-colors flex items-center justify-between group"
                                onClick={() => navigate(`/complaints/${c.complaint_id}`)}
                            >
                                <div className="flex items-start gap-4">
                                    <div className={`mt-1 p-2 rounded-lg ${c.severity === 'critical' ? 'bg-red-50 text-red-600 border border-red-100' :
                                            c.severity === 'high' ? 'bg-orange-50 text-orange-600 border border-orange-100' :
                                                c.severity === 'medium' ? 'bg-amber-50 text-amber-600 border border-amber-100' :
                                                    'bg-blue-50 text-blue-600 border border-blue-100'
                                        }`}>
                                        <AlertCircle className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-slate-900 group-hover:text-primary-600 transition-colors">{c.subject}</h4>
                                        <div className="flex items-center gap-4 mt-1 text-sm text-slate-500 font-medium">
                                            <span>{c.customer_name}</span>
                                            <span className="text-slate-300">•</span>
                                            <span className="flex items-center gap-1">
                                                <Clock className="w-3 h-3" />
                                                {new Date(c.created_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <span className={`px-3 py-1 rounded-full text-xs font-bold border uppercase tracking-wide ${c.status === 'new' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                                        c.status === 'resolved' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                                            'bg-purple-50 text-purple-700 border-purple-200'
                                    }`}>
                                    {c.status.replace('_', ' ')}
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Edit Modal Reuse */}
            {showEditModal && (
                <CreateUserModal
                    isOpen={showEditModal}
                    onClose={() => setShowEditModal(false)}
                    initialData={user}
                    isEdit={true}
                    onCreate={async (data) => {
                        try {
                            await userService.updateUser(user.user_id, data);
                            await fetchData(); // Reload data
                            setShowEditModal(false);
                        } catch (err) {
                            console.error("Failed to update user", err);
                            alert("Failed to update user");
                        }
                    }}
                />
            )}
        </div>
    );
}
