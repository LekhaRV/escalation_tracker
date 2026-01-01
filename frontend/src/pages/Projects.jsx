import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Users, Plus } from 'lucide-react';
import { projectService } from '../services/projectService';
import { CreateProjectModal } from '../components/common/Modals';

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
                    <h1 className="text-2xl font-bold text-white">Projects</h1>
                    <p className="text-gray-400 text-sm">Manage projects and teams</p>
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
                    <p className="text-gray-400">Loading projects...</p>
                ) : projects.map((project) => (
                    <div
                        key={project.project_id}
                        className="card group cursor-pointer hover:border-primary-500/30"
                        onClick={() => navigate(`/projects/${project.project_id}`)}
                    >
                        <div className="flex justify-between items-start mb-4">
                            <div className="p-3 bg-white/5 rounded-lg text-primary-400 group-hover:bg-primary-500/20 group-hover:text-primary-300 transition-colors">
                                <Briefcase className="w-6 h-6" />
                            </div>
                            <span className={`px-2 py-1 rounded text-xs font-medium uppercase ${project.status === 'active' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-gray-500/10 text-gray-400'
                                }`}>
                                {project.status}
                            </span>
                        </div>

                        <h3 className="text-lg font-bold text-white mb-1 group-hover:text-primary-400 transition-colors">
                            {project.project_name}
                        </h3>
                        <div className="flex justify-between items-center mb-4">
                            <p className="text-sm text-gray-400">{project.client_name}</p>
                            <span className="text-xs px-2 py-0.5 rounded bg-white/5 text-gray-400 border border-white/5">
                                {project.department_name}
                            </span>
                        </div>

                        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/5">
                            <div>
                                <span className="block text-xs text-gray-500 uppercase mb-1">Active Complaints</span>
                                <span className="block text-xl font-bold text-white">{project.complaints_count || 0}</span>
                            </div>
                            <div>
                                <span className="block text-xs text-gray-500 uppercase mb-1">Team Size</span>
                                <div className="flex items-center gap-2">
                                    <span className="block text-xl font-bold text-white">{project.team_count || 0}</span>
                                    <Users className="w-4 h-4 text-gray-600" />
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
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
