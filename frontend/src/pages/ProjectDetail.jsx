import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Users, Briefcase, Calendar, Plus } from 'lucide-react';
import { projectService } from '../services/projectService';
import { AddMemberModal } from '../components/common/Modals';

function ProjectDetail() {
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

    if (loading) return <div>Loading...</div>;
    if (!project) return <div>Project not found</div>;

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center gap-4">
                <button
                    onClick={() => navigate('/projects')}
                    className="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white"
                >
                    <ArrowLeft className="w-5 h-5" />
                </button>
                <div>
                    <h1 className="text-xl font-bold text-white">{project.project_name}</h1>
                    <p className="text-gray-400 text-sm">{project.client_name}</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Info Card */}
                <div className="card h-fit">
                    <h2 className="text-lg font-bold text-white mb-4">Project Overview</h2>
                    <div className="space-y-4">
                        <div>
                            <label className="text-xs text-gray-500 uppercase">Project Code</label>
                            <p className="text-white font-mono">{project.project_code}</p>
                        </div>
                        <div>
                            <label className="text-xs text-gray-500 uppercase">Department</label>
                            <p className="text-white">{project.department_name || 'N/A'}</p>
                        </div>
                        <div>
                            <label className="text-xs text-gray-500 uppercase">Project Manager</label>
                            <p className="text-white">{project.project_manager_name || 'N/A'}</p>
                        </div>
                        <div>
                            <label className="text-xs text-gray-500 uppercase">Team Lead</label>
                            <p className="text-white">{project.team_lead_name || 'N/A'}</p>
                        </div>
                        <div>
                            <label className="text-xs text-gray-500 uppercase">Timeline</label>
                            <p className="text-sm text-gray-300">
                                {project.start_date} - {project.end_date || 'Ongoing'}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Team Members */}
                <div className="lg:col-span-2 card">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-lg font-bold text-white">Team Members</h2>
                        <button
                            onClick={() => setIsModalOpen(true)}
                            className="btn-secondary text-sm flex items-center gap-2"
                        >
                            <Plus className="w-4 h-4" /> Add Member
                        </button>
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
                                <tr className="text-xs text-gray-500 uppercase border-b border-white/5">
                                    <th className="pb-3 pl-2">Name</th>
                                    <th className="pb-3">Role</th>
                                    <th className="pb-3">Specialization</th>
                                    <th className="pb-3">Workload</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {project.team_members.map((member) => (
                                    <tr key={member.id} className="text-sm">
                                        <td className="py-3 pl-2 text-white font-medium">{member.user_name}</td>
                                        <td className="py-3 text-gray-400">{member.role}</td>
                                        <td className="py-3">
                                            <div className="flex flex-wrap gap-1">
                                                {member.specialization?.map(s => (
                                                    <span key={s} className="px-1.5 py-0.5 bg-white/5 rounded text-xs text-gray-300">
                                                        {s}
                                                    </span>
                                                ))}
                                            </div>
                                        </td>
                                        <td className="py-3">
                                            <div className="w-24 bg-white/5 rounded-full h-1.5 overflow-hidden">
                                                <div
                                                    className="bg-primary-500 h-full rounded-full"
                                                    style={{ width: `${(member.current_workload / member.workload_capacity) * 100}%` }}
                                                />
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
