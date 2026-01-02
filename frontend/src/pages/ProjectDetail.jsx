import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Users, Briefcase, Calendar, Plus, Pencil, Trash } from 'lucide-react';
import { projectService } from '../services/projectService';
import { TeamMemberModal, ProjectModal, ConfirmationModal } from '../components/common/Modals';

function ProjectDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);

    const [isAddMemberOpen, setIsAddMemberOpen] = useState(false);
    const [isEditProjectOpen, setIsEditProjectOpen] = useState(false);

    // Team management state
    const [editMemberData, setEditMemberData] = useState(null);
    const [isEditMemberOpen, setIsEditMemberOpen] = useState(false);
    const [memberToRemove, setMemberToRemove] = useState(null);
    const [isRemoveMemberOpen, setIsRemoveMemberOpen] = useState(false);

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

    const handleUpdateProject = async (data) => {
        try {
            await projectService.updateProject(id, data);
            setIsEditProjectOpen(false);
            fetchDetail();
        } catch (error) {
            console.error(error);
            alert('Failed to update project');
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
            setIsAddMemberOpen(false);
            fetchDetail();
        } catch (error) {
            console.error(error);
            alert('Failed to add team member: ' + (error.response?.data?.detail || error.message));
        }
    };

    const handleUpdateMember = async (memberData) => {
        try {
            await projectService.manageTeam(id, {
                user_id: memberData.user_id,
                action: 'update',
                role: memberData.role,
                specialization: memberData.specialization
            });
            setIsEditMemberOpen(false);
            fetchDetail();
        } catch (error) {
            console.error(error);
            alert('Failed to update member');
        }
    };

    const confirmRemoveMember = async () => {
        if (!memberToRemove) return;
        try {
            await projectService.manageTeam(id, {
                user_id: memberToRemove.user_id,
                action: 'remove'
            });
            setIsRemoveMemberOpen(false);
            setMemberToRemove(null);
            fetchDetail();
        } catch (error) {
            console.error(error);
            alert('Failed to remove member');
        }
    };

    const openEditMember = (member) => {
        setEditMemberData(member);
        setIsEditMemberOpen(true);
    };

    const openRemoveMember = (member) => {
        setMemberToRemove(member);
        setIsRemoveMemberOpen(true);
    };

    if (loading) return <div>Loading...</div>;
    if (!project) return <div>Project not found</div>;

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => navigate('/projects')}
                        className="p-2 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-slate-900"
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div>
                        <h1 className="text-xl font-bold text-slate-900">{project.project_name}</h1>
                        <p className="text-slate-500 text-sm">{project.client_name}</p>
                    </div>
                </div>
                <button
                    onClick={() => setIsEditProjectOpen(true)}
                    className="btn-secondary flex items-center gap-2"
                >
                    <Pencil className="w-4 h-4" />
                    <span>Edit Project</span>
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Info Card */}
                <div className="card h-fit">
                    <h2 className="text-lg font-bold text-slate-900 mb-4">Project Overview</h2>
                    <div className="space-y-4">
                        <div>
                            <label className="text-xs text-slate-500 uppercase">Project Code</label>
                            <p className="text-slate-900 font-mono">{project.project_code}</p>
                        </div>
                        <div>
                            <label className="text-xs text-slate-500 uppercase">Department</label>
                            <p className="text-slate-900">{project.department_name || 'N/A'}</p>
                        </div>
                        <div>
                            <label className="text-xs text-slate-500 uppercase">Project Manager</label>
                            <p className="text-slate-900">{project.project_manager_name || 'N/A'}</p>
                        </div>
                        <div>
                            <label className="text-xs text-slate-500 uppercase">Team Lead</label>
                            <p className="text-slate-900">{project.team_lead_name || 'N/A'}</p>
                        </div>
                        <div>
                            <label className="text-xs text-slate-500 uppercase">Timeline</label>
                            <p className="text-sm text-slate-600">
                                {project.start_date} - {project.end_date || 'Ongoing'}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Team Members */}
                <div className="lg:col-span-2 card">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-lg font-bold text-slate-900">Team Members</h2>
                        <button
                            onClick={() => setIsAddMemberOpen(true)}
                            className="btn-secondary text-sm flex items-center gap-2"
                        >
                            <Plus className="w-4 h-4" /> Add Member
                        </button>
                    </div>

                    <TeamMemberModal
                        isOpen={isAddMemberOpen}
                        onClose={() => setIsAddMemberOpen(false)}
                        onSubmit={handleAddMember}
                        departmentId={project.department_id}
                    />

                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="text-xs text-slate-500 uppercase border-b border-slate-200">
                                    <th className="pb-3 pl-2">Name</th>
                                    <th className="pb-3">Role</th>
                                    <th className="pb-3">Specialization</th>
                                    <th className="pb-3">Workload</th>
                                    <th className="pb-3 w-20">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {project.team_members.map((member) => (
                                    <tr key={member.id} className="text-sm">
                                        <td className="py-3 pl-2 text-slate-900 font-medium">{member.user_name}</td>
                                        <td className="py-3 text-slate-500">{member.role}</td>
                                        <td className="py-3">
                                            <div className="flex flex-wrap gap-1">
                                                {member.specialization?.map(s => (
                                                    <span key={s} className="px-1.5 py-0.5 bg-slate-100 rounded text-xs text-slate-600">
                                                        {s}
                                                    </span>
                                                ))}
                                            </div>
                                        </td>
                                        <td className="py-3">
                                            <div className="w-24 bg-slate-200 rounded-full h-1.5 overflow-hidden">
                                                <div
                                                    className="bg-blue-600 h-full rounded-full"
                                                    style={{ width: `${(member.current_workload / member.workload_capacity) * 100}%` }}
                                                />
                                            </div>
                                        </td>
                                        <td className="py-3">
                                            <div className="flex items-center gap-2">
                                                <button
                                                    onClick={() => openEditMember(member)}
                                                    className="p-1 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                                                    title="Edit Role"
                                                >
                                                    <Pencil className="w-4 h-4" />
                                                </button>
                                                <button
                                                    onClick={() => openRemoveMember(member)}
                                                    className="p-1 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                                                    title="Remove Member"
                                                >
                                                    <Trash className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>


            {/* Edit Project Modal */}
            <ProjectModal
                isOpen={isEditProjectOpen}
                onClose={() => setIsEditProjectOpen(false)}
                onSubmit={handleUpdateProject}
                initialData={project}
                isEdit={true}
            />

            {/* Edit Member Modal */}
            {
                editMemberData && (
                    <TeamMemberModal
                        isOpen={isEditMemberOpen}
                        onClose={() => setIsEditMemberOpen(false)}
                        onSubmit={handleUpdateMember}
                        departmentId={project.department_id}
                        initialData={editMemberData}
                        isEdit={true}
                    />
                )
            }

            {/* Remove Confirmation */}
            <ConfirmationModal
                isOpen={isRemoveMemberOpen}
                onClose={() => setIsRemoveMemberOpen(false)}
                onConfirm={confirmRemoveMember}
                title="Remove Team Member"
                message={`Are you sure you want to remove ${memberToRemove?.user_name} from this project?`}
                confirmText="Remove"
                isDangerous={true}
            />
        </div >
    );
}

export default ProjectDetail;
