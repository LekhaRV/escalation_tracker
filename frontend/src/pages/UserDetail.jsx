import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/common/Layout';
import { userService } from '../services/userService';
import { complaintService } from '../services/complaintService';
import { ArrowLeft, Mail, Building, Shield, User as UserIcon, AlertCircle, Clock } from 'lucide-react';
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
        <Layout>
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        </Layout>
    );

    if (error || !user) return (
        <Layout>
            <div className="p-8 text-center">
                <div className="text-red-500 mb-2">{error || "User not found"}</div>
                <button
                    onClick={() => navigate('/users')}
                    className="text-blue-500 hover:underline"
                >
                    Back to Users
                </button>
            </div>
        </Layout>
    );

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
                <button onClick={() => navigate('/users')} className="p-2 hover:bg-slate-100 rounded-full transition-colors">
                    <ArrowLeft className="w-6 h-6 text-slate-500" />
                </button>
                <h1 className="text-2xl font-bold text-slate-900">User Details</h1>
            </div>

            {/* Profile Card */}
            <div className="bg-white border border-slate-200 shadow-sm rounded-xl p-8">
                <div className="flex flex-col md:flex-row gap-8 items-start">
                    {/* Avatar */}
                    <div className="w-24 h-24 rounded-full bg-blue-50 flex items-center justify-center text-blue-600 font-bold text-4xl shrink-0">
                        {user.name.charAt(0).toUpperCase()}
                    </div>

                    {/* Info */}
                    <div className="flex-1 space-y-4">
                        <div className="flex items-start justify-between">
                            <div>
                                <h2 className="text-2xl font-bold text-slate-900 mb-1">{user.name}</h2>
                                <div className="flex items-center gap-2 text-slate-500">
                                    <Mail className="w-4 h-4" />
                                    <span>{user.email}</span>
                                </div>
                            </div>
                            <button
                                onClick={() => setShowEditModal(true)}
                                className="px-4 py-2 bg-white hover:bg-slate-50 text-slate-700 rounded-lg transition-colors border border-slate-200 shadow-sm"
                            >
                                Edit Profile
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-slate-100">
                            <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                                <Shield className="w-5 h-5 text-purple-500" />
                                <div>
                                    <div className="text-xs text-slate-500 uppercase font-semibold">Role</div>
                                    <div className="text-sm font-medium text-slate-900 capitalize">{user.role}</div>
                                </div>
                            </div>
                            <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                                <Building className="w-5 h-5 text-blue-500" />
                                <div>
                                    <div className="text-xs text-slate-500 uppercase font-semibold">Department</div>
                                    <div className="text-sm font-medium text-slate-900">{user.department_name || "N/A"}</div>
                                </div>
                            </div>
                            <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                                <UserIcon className="w-5 h-5 text-green-500" />
                                <div>
                                    <div className="text-xs text-slate-500 uppercase font-semibold">Status</div>
                                    <div className="text-sm font-medium text-slate-900 capitalize">{user.status}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Assigned Complaints */}
            <div className="bg-white border border-slate-200 shadow-sm rounded-xl overflow-hidden">
                <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                    <h3 className="font-bold text-lg text-slate-900">Assigned Escalations (Complaints)</h3>
                    <span className="px-2 py-1 bg-slate-100 rounded text-xs text-slate-600 font-medium">{complaints.length} Total</span>
                </div>

                {complaints.length === 0 ? (
                    <div className="p-12 text-center text-slate-500">No complaints currently assigned.</div>
                ) : (
                    <div className="divide-y divide-slate-100">
                        {complaints.map(c => (
                            <div
                                key={c.complaint_id}
                                className="p-4 hover:bg-slate-50 cursor-pointer transition-colors flex items-center justify-between group"
                                onClick={() => navigate(`/complaints/${c.complaint_id}`)}
                            >
                                <div className="flex items-start gap-4">
                                    <div className={`mt-1 p-2 rounded-lg ${c.severity === 'critical' || c.severity === 'high' ? 'bg-red-50 text-red-600' :
                                            c.severity === 'medium' ? 'bg-orange-50 text-orange-600' : 'bg-blue-50 text-blue-600'
                                        }`}>
                                        <AlertCircle className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h4 className="font-medium text-slate-900 group-hover:text-blue-600 transition-colors">{c.subject}</h4>
                                        <div className="flex items-center gap-4 mt-1 text-sm text-slate-500">
                                            <span>{c.customer_name}</span>
                                            <span>•</span>
                                            <span className="flex items-center gap-1">
                                                <Clock className="w-3 h-3" />
                                                {new Date(c.created_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <span className={`px-3 py-1 rounded-full text-xs font-medium border uppercase ${c.status === 'new' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                                        c.status === 'resolved' ? 'bg-green-50 text-green-700 border-green-200' :
                                            'bg-yellow-50 text-yellow-700 border-yellow-200'
                                    }`}>
                                    {c.status}
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
