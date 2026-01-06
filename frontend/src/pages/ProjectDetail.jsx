import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Users, Briefcase, Calendar, Plus } from 'lucide-react';
import { projectService } from '../services/projectService';
import { AddMemberModal } from '../components/common/Modals';

function ProjectDetail() {
    const { user } = useAuth();
    const { id } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);

    const [isModalOpen, setIsModalOpen] = useState(false);

    useEffect(() => {
        fetchDetail();
    }, [id]);

    const fetchDetail = async () => {
        try {
            const data = await projectService.getProject(id);
            setProject(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleAddMember = async (memberData) => {
        try {
            await projectService.manageTeam(id, {
                user_id: memberData.user_id,
                action: 'add',
                role: memberData.role,
                specialization: memberData.specialization
            });
            setIsModalOpen(false);
            fetchDetail();
        } catch (error) {
            console.error(error);
            alert('Failed to add team member: ' + (error.response?.data?.detail || error.message));
        }
    };

    if (loading) return (
        <div className="flex justify-center items-center h-64 text-slate-600 font-medium">
            Loading Project...
        </div>
    );
    if (!project) return <div className="p-8 text-center text-slate-600">Project not found</div>;

    return (
        <div className="space-y-6 animate-fade-in max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center gap-4">
                <button
                    onClick={() => navigate('/projects')}
                    className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-slate-900 transition-colors"
                >
                    <ArrowLeft className="w-5 h-5" />
                </button>
                <div>
                    <h1 className="text-xl font-bold text-slate-900">{project.project_name}</h1>
                    <p className="text-slate-500 text-sm font-medium">{project.client_name}</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Info Card */}
                <div className="card bg-white border border-slate-200 shadow-sm p-6 rounded-xl h-fit">
                    <h2 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
                        <Briefcase className="w-5 h-5 text-primary-600" />
                        Project Overview
                    </h2>
                    <div className="space-y-5">
                        <div className="pb-4 border-b border-slate-100 last:border-0 last:pb-0">
                            <label className="text-xs text-slate-500 font-semibold uppercase mb-1 block">Project Code</label>
                            <p className="text-slate-700 font-mono bg-slate-50 px-2 py-1 rounded w-fit text-sm">{project.project_code}</p>
                        </div>
                        <div className="pb-4 border-b border-slate-100 last:border-0 last:pb-0">
                            <label className="text-xs text-slate-500 font-semibold uppercase mb-1 block">Department</label>
                            <p className="text-slate-900 font-medium">{project.department_name || 'N/A'}</p>
                        </div>
                        <div className="pb-4 border-b border-slate-100 last:border-0 last:pb-0">
                            <label className="text-xs text-slate-500 font-semibold uppercase mb-1 block">Project Manager</label>
                            <p className="text-slate-900 font-medium">{project.project_manager_name || 'N/A'}</p>
                        </div>
                        <div className="pb-4 border-b border-slate-100 last:border-0 last:pb-0">
                            <label className="text-xs text-slate-500 font-semibold uppercase mb-1 block">Team Lead</label>
                            <p className="text-slate-900 font-medium">{project.team_lead_name || 'N/A'}</p>
                        </div>
                        <div className="pb-4 border-b border-slate-100 last:border-0 last:pb-0">
                            <label className="text-xs text-slate-500 font-semibold uppercase mb-1 block">Timeline</label>
                            <div className="flex items-center gap-2 text-sm text-slate-700">
                                <Calendar className="w-4 h-4 text-slate-400" />
                                <span>{project.start_date}</span>
                                <span className="text-slate-400">→</span>
                                <span>{project.end_date || 'Ongoing'}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Team Members */}
                <div className="lg:col-span-2 card bg-white border border-slate-200 shadow-sm p-6 rounded-xl">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                            <Users className="w-5 h-5 text-primary-600" />
                            Team Members
                        </h2>
                        {['admin', 'manager'].includes(user?.role) && (
                            <button
                                onClick={() => setIsModalOpen(true)}
                                className="btn-secondary text-sm flex items-center gap-2 py-2 px-3 h-auto"
                            >
                                <Plus className="w-4 h-4" /> Add Member
                            </button>
                        )}
                    </div>

                    <AddMemberModal
                        isOpen={isModalOpen}
                        onClose={() => setIsModalOpen(false)}
                        onAdd={handleAddMember}
                        departmentId={project.department_id}
                    />

                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="text-xs text-slate-500 font-semibold uppercase border-b border-slate-200 bg-slate-50/50">
                                    <th className="py-3 pl-3 rounded-l-lg">Name</th>
                                    <th className="py-3">Role</th>
                                    <th className="py-3">Specialization</th>
                                    <th className="py-3 pr-3 rounded-r-lg w-32">Workload</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {project.team_members.map((member) => (
                                    <tr key={member.id} className="text-sm hover:bg-slate-50/80 transition-colors">
                                        <td className="py-3 pl-3 text-slate-900 font-semibold">{member.user_name}</td>
                                        <td className="py-3 text-slate-600">{member.role}</td>
                                        <td className="py-3">
                                            <div className="flex flex-wrap gap-1">
                                                {member.specialization?.map(s => (
                                                    <span key={s} className="px-2 py-0.5 bg-slate-100 border border-slate-200 rounded text-xs text-slate-600 font-medium">
                                                        {s}
                                                    </span>
                                                ))}
                                            </div>
                                        </td>
                                        <td className="py-3 pr-3">
                                            <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                                                <div
                                                    className="bg-primary-500 h-full rounded-full"
                                                    style={{ width: `${Math.min((member.current_workload / member.workload_capacity) * 100, 100)}%` }}
                                                />
                                            </div>
                                            <div className="text-xs text-slate-400 mt-1 text-right">
                                                {Math.round((member.current_workload / member.workload_capacity) * 100)}% Used
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ProjectDetail;
