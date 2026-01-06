import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Users, Plus, TrendingUp, AlertTriangle, FolderOpen, ArrowRight } from 'lucide-react';
import { projectService } from '../services/projectService';
import { CreateProjectModal } from '../components/common/Modals';

function Projects() {
    const { user } = useAuth();
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const [isModalOpen, setIsModalOpen] = useState(false);

    useEffect(() => {
        fetchProjects();
    }, []);

    const fetchProjects = async () => {
        try {
            const data = await projectService.getProjects();
            setProjects(data.items);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateProject = async (data) => {
        try {
            await projectService.createProject(data);
            setIsModalOpen(false);
            fetchProjects();
        } catch (error) {
            console.error(error);
            alert('Failed to create project');
        }
    };

    // Calculate stats
    const activeProjects = projects.filter(p => p.status === 'active').length;
    const totalComplaints = projects.reduce((sum, p) => sum + (p.complaints_count || 0), 0);
    const totalTeamMembers = projects.reduce((sum, p) => sum + (p.team_count || 0), 0);

    // Color palette for project cards
    const cardColors = [
        { bg: 'from-blue-500 to-indigo-600', light: 'bg-blue-50', text: 'text-blue-600' },
        { bg: 'from-violet-500 to-purple-600', light: 'bg-violet-50', text: 'text-violet-600' },
        { bg: 'from-emerald-500 to-teal-600', light: 'bg-emerald-50', text: 'text-emerald-600' },
        { bg: 'from-amber-500 to-orange-600', light: 'bg-amber-50', text: 'text-amber-600' },
        { bg: 'from-rose-500 to-pink-600', light: 'bg-rose-50', text: 'text-rose-600' },
        { bg: 'from-cyan-500 to-blue-600', light: 'bg-cyan-50', text: 'text-cyan-600' },
    ];

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex justify-between items-start">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg shadow-violet-500/25">
                        <Briefcase className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-slate-800">Projects</h1>
                        <p className="text-slate-500 text-sm">Manage projects and track performance</p>
                    </div>
                </div>
                {['ADMIN', 'MANAGER'].includes(user?.role) && (
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-xl font-semibold shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all"
                    >
                        <Plus className="w-4 h-4" />
                        <span>New Project</span>
                    </button>
                )}
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-4 gap-4">
                <div className="bg-white rounded-xl border border-slate-200 p-5 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-violet-100 flex items-center justify-center">
                        <FolderOpen className="w-6 h-6 text-violet-600" />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-slate-800">{projects.length}</p>
                        <p className="text-sm text-slate-500">Total Projects</p>
                    </div>
                </div>
                <div className="bg-white rounded-xl border border-slate-200 p-5 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center">
                        <TrendingUp className="w-6 h-6 text-emerald-600" />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-slate-800">{activeProjects}</p>
                        <p className="text-sm text-slate-500">Active</p>
                    </div>
                </div>
                <div className="bg-white rounded-xl border border-slate-200 p-5 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center">
                        <AlertTriangle className="w-6 h-6 text-amber-600" />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-slate-800">{totalComplaints}</p>
                        <p className="text-sm text-slate-500">Open Issues</p>
                    </div>
                </div>
                <div className="bg-white rounded-xl border border-slate-200 p-5 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
                        <Users className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-slate-800">{totalTeamMembers}</p>
                        <p className="text-sm text-slate-500">Team Members</p>
                    </div>
                </div>
            </div>

            {/* Project Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {loading ? (
                    <p className="text-slate-500 text-center col-span-3 py-12">Loading projects...</p>
                ) : projects.map((project, idx) => {
                    const color = cardColors[idx % cardColors.length];
                    return (
                        <div
                            key={project.project_id}
                            className="bg-white border border-slate-200 rounded-2xl overflow-hidden group cursor-pointer hover:shadow-xl hover:border-slate-300 transition-all"
                            onClick={() => navigate(`/projects/${project.project_id}`)}
                        >
                            {/* Colored Header */}
                            <div className={`h-2 bg-gradient-to-r ${color.bg}`} />

                            <div className="p-6">
                                <div className="flex justify-between items-start mb-4">
                                    <div className={`p-3 rounded-xl ${color.light} ${color.text} group-hover:scale-110 transition-transform`}>
                                        <Briefcase className="w-6 h-6" />
                                    </div>
                                    <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${project.status === 'active'
                                            ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                                            : 'bg-slate-100 text-slate-500 border border-slate-200'
                                        }`}>
                                        {project.status}
                                    </span>
                                </div>

                                <h3 className="text-lg font-bold text-slate-800 mb-1 group-hover:text-violet-600 transition-colors">
                                    {project.project_name}
                                </h3>
                                <p className="text-sm text-slate-500 mb-4">{project.client_name}</p>

                                {project.department_name && (
                                    <span className="inline-block text-xs px-2.5 py-1 rounded-lg bg-slate-100 text-slate-600 font-medium mb-4">
                                        {project.department_name}
                                    </span>
                                )}

                                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-100">
                                    <div className="text-center p-3 bg-slate-50 rounded-xl">
                                        <p className="text-xl font-bold text-slate-800">{project.complaints_count || 0}</p>
                                        <p className="text-xs text-slate-500 font-medium">Issues</p>
                                    </div>
                                    <div className="text-center p-3 bg-slate-50 rounded-xl">
                                        <p className="text-xl font-bold text-slate-800">{project.team_count || 0}</p>
                                        <p className="text-xs text-slate-500 font-medium">Team</p>
                                    </div>
                                </div>

                                <button className="w-full mt-4 py-2.5 text-sm font-semibold text-slate-600 hover:text-violet-600 flex items-center justify-center gap-2 group-hover:gap-3 transition-all">
                                    View Details <ArrowRight className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>

            <CreateProjectModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onCreate={handleCreateProject}
            />
        </div>
    );
}

export default Projects;
