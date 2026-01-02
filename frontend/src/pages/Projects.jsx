import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Users, Plus } from 'lucide-react';
import { projectService } from '../services/projectService';
import { ProjectModal } from '../components/common/Modals';

function Projects() {
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

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Projects</h1>
                    <p className="text-slate-500 text-sm">Manage projects and teams</p>
                </div>
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="btn-primary flex items-center gap-2"
                >
                    <Plus className="w-4 h-4" />
                    <span>New Project</span>
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {loading ? (
                    <p className="text-slate-500">Loading projects...</p>
                ) : projects.map((project) => (
                    <div
                        key={project.project_id}
                        className="card group cursor-pointer hover:border-blue-500/30 hover:shadow-md transition-all"
                        onClick={() => navigate(`/projects/${project.project_id}`)}
                    >
                        <div className="flex justify-between items-start mb-4">
                            <div className="p-3 bg-blue-50 rounded-lg text-blue-600 group-hover:bg-blue-100 group-hover:text-blue-700 transition-colors">
                                <Briefcase className="w-6 h-6" />
                            </div>
                            <span className={`px-2 py-1 rounded text-xs font-medium uppercase ${project.status === 'active' ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' : 'bg-slate-100 text-slate-500'
                                }`}>
                                {project.status}
                            </span>
                        </div>

                        <h3 className="text-lg font-bold text-slate-900 mb-1 group-hover:text-blue-600 transition-colors">
                            {project.project_name}
                        </h3>
                        <div className="flex justify-between items-center mb-4">
                            <p className="text-sm text-slate-500">{project.client_name}</p>
                            <span className="text-xs px-2 py-0.5 rounded bg-slate-50 text-slate-500 border border-slate-200">
                                {project.department_name}
                            </span>
                        </div>

                        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-200">
                            <div>
                                <span className="block text-xs text-slate-400 uppercase mb-1">Active Complaints</span>
                                <span className="block text-xl font-bold text-slate-900">{project.complaints_count || 0}</span>
                            </div>
                            <div>
                                <span className="block text-xs text-slate-400 uppercase mb-1">Team Size</span>
                                <div className="flex items-center gap-2">
                                    <span className="block text-xl font-bold text-slate-900">{project.team_count || 0}</span>
                                    <Users className="w-4 h-4 text-slate-400" />
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <ProjectModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSubmit={handleCreateProject}
            />
        </div>
    );
}

export default Projects;
