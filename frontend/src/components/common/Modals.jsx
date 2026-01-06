import { useState, useEffect } from 'react';
import { X, Save, Sparkles } from 'lucide-react';

export function Modal({ isOpen, onClose, title, children }) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
            <div className="relative bg-[#0f172a] border border-white/10 rounded-xl shadow-2xl w-full max-w-lg overflow-hidden animate-scale-in">
                <div className="flex items-center justify-between p-4 border-b border-white/5">
                    <h2 className="text-lg font-bold text-white">{title}</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>
                <div className="p-6">
                    {children}
                </div>
            </div>
        </div>
    );
}

export function CreateProjectModal({ isOpen, onClose, onCreate }) {
    const [departments, setDepartments] = useState([]);
    const [formData, setFormData] = useState({
        project_name: '',
        project_code: '',
        client_name: '',
        description: '',
        department_id: ''
    });

    useEffect(() => {
        if (isOpen) {
            fetchDepartments();
        }
    }, [isOpen]);

    const fetchDepartments = async () => {
        try {
            // Fetch default org first (or use current user's org if available in context)
            // Ideally should be passed as prop or from context. 
            // For now, let's fetch default org to be safe/consistent with Login.
            // Better: Import authService
            const { authService } = await import('../../services/authService');
            const { departmentService } = await import('../../services/departmentService');

            const org = await authService.getDefaultOrg();
            const depts = await departmentService.getAll(org.org_id);
            setDepartments(depts);
        } catch (error) {
            console.error("Failed to fetch departments", error);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onCreate(formData);
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Create New Project">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Project Name</label>
                    <input
                        type="text"
                        required
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.project_name}
                        onChange={e => setFormData({ ...formData, project_name: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Project Code</label>
                    <input
                        type="text"
                        required
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.project_code}
                        onChange={e => setFormData({ ...formData, project_code: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Department</label>
                    <select
                        required
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.department_id}
                        onChange={e => setFormData({ ...formData, department_id: e.target.value })}
                    >
                        <option value="" disabled>Select Department</option>
                        {departments.map(dept => (
                            <option key={dept.department_id} value={dept.department_id}>{dept.name}</option>
                        ))}
                    </select>
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Client Name</label>
                    <input
                        type="text"
                        required
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.client_name}
                        onChange={e => setFormData({ ...formData, client_name: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Description</label>
                    <textarea
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        rows="3"
                        value={formData.description}
                        onChange={e => setFormData({ ...formData, description: e.target.value })}
                    />
                </div>
                <div className="flex justify-end pt-4">
                    <button type="submit" className="btn-primary flex items-center gap-2">
                        <Save className="w-4 h-4" />
                        <span>Create Project</span>
                    </button>
                </div>
            </form>
        </Modal>
    );
}

export function AddMemberModal({ isOpen, onClose, onAdd, departmentId }) {
    const [users, setUsers] = useState([]);
    const [formData, setFormData] = useState({
        user_id: '',
        role: 'Developer',
        specialization: ''
    });

    useEffect(() => {
        if (isOpen && departmentId) {
            fetchUsers();
        }
    }, [isOpen, departmentId]);

    const fetchUsers = async () => {
        try {
            const { userService } = await import('../../services/userService');
            // Fetch users for the specific department
            // Note: We need to ensure userService.getUsers supports department_id param or we filter client side.
            // The backend endpoint /admin/users doesn't explicitly list department_id in filters in my read earlier, 
            // but let's check if we can filter client side if needed.
            // Actually, backend /admin/users takes 'role', 'team', 'status'. Not department.
            // But we can filter client side for now or add params.
            // Wait, for Managers, they can only see their department users usually? 
            // Let's simplified: fetch all and filter.
            const data = await userService.getUsers();
            // Filter by department
            const deptUsers = data.items.filter(u => u.department_id === departmentId && u.role !== 'VIEWER');
            setUsers(deptUsers);
        } catch (error) {
            console.error("Failed to fetch users", error);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onAdd({
            ...formData,
            specialization: formData.specialization.split(',').map(s => s.trim())
        });
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Add Team Member">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Select User</label>
                    <select
                        required
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.user_id}
                        onChange={e => setFormData({ ...formData, user_id: e.target.value })}
                    >
                        <option value="">Select User</option>
                        {users.map(u => (
                            <option key={u.user_id} value={u.user_id}>{u.name} ({u.email})</option>
                        ))}
                    </select>
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Role</label>
                    <select
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.role}
                        onChange={e => setFormData({ ...formData, role: e.target.value })}
                    >
                        <option value="Developer">Developer</option>
                        <option value="Tester">Tester</option>
                        <option value="DevOps">DevOps</option>
                        <option value="Designer">Designer</option>
                        <option value="Manager">Manager</option>
                    </select>
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Specialization (comma separated)</label>
                    <input
                        type="text"
                        placeholder="React, Python, AWS"
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.specialization}
                        onChange={e => setFormData({ ...formData, specialization: e.target.value })}
                    />
                </div>
                <div className="flex justify-end pt-4">
                    <button type="submit" className="btn-primary flex items-center gap-2">
                        <Save className="w-4 h-4" />
                        <span>Add Member</span>
                    </button>
                </div>
            </form>
        </Modal>
    );
}

export function CreateComplaintModal({ isOpen, onClose, onCreate }) {
    const [projects, setProjects] = useState([]);
    const [formData, setFormData] = useState({
        subject: '',
        description: '',
        customer_name: '',
        customer_email: '',
        priority: 'medium',
        project_id: ''
    });

    useEffect(() => {
        if (isOpen) {
            fetchProjects();
        }
    }, [isOpen]);

    const fetchProjects = async () => {
        try {
            const { projectService } = await import('../../services/projectService');
            // Assuming we want all projects to be selectable
            // We need to fetch current user's org id.
            const { authService } = await import('../../services/authService');
            const org = await authService.getDefaultOrg();

            // Get all projects
            const data = await projectService.getProjects(org.org_id);
            setProjects(data.items);
        } catch (error) {
            console.error("Failed to fetch projects", error);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onCreate(formData);
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Create New Complaint">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Subject</label>
                    <input
                        type="text"
                        required
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.subject}
                        onChange={e => setFormData({ ...formData, subject: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Description</label>
                    <textarea
                        required
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        rows="4"
                        value={formData.description}
                        onChange={e => setFormData({ ...formData, description: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Customer Name</label>
                    <input
                        type="text"
                        required
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.customer_name}
                        onChange={e => setFormData({ ...formData, customer_name: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Customer Email</label>
                    <input
                        type="email"
                        required
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.customer_email}
                        onChange={e => setFormData({ ...formData, customer_email: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Priority</label>
                    <select
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.priority}
                        onChange={e => setFormData({ ...formData, priority: e.target.value })}
                    >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                    </select>
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Project</label>
                    <select
                        required
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.project_id}
                        onChange={e => setFormData({ ...formData, project_id: e.target.value })}
                    >
                        <option value="">Select Project</option>
                        {projects.map(p => (
                            <option key={p.project_id} value={p.project_id}>{p.project_name}</option>
                        ))}
                    </select>
                </div>
                <div className="flex justify-end pt-4">
                    <button type="submit" className="btn-primary flex items-center gap-2">
                        <Save className="w-4 h-4" />
                        <span>Create Complaint</span>
                    </button>
                </div>
            </form>
        </Modal >
    );
}

export function SimulateEmailModal({ isOpen, onClose, onSend }) {
    const [formData, setFormData] = useState({
        sender: 'customer@example.com',
        subject: '',
        content: ''
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        onSend(formData);
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Simulate Incoming Email">
            <div className="mb-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg text-sm text-blue-200">
                This tool sends a fake email to the backend to test the AI processing pipeline without needing a real SMTP connection.
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm text-gray-400 mb-1">From (Sender Email)</label>
                    <input
                        type="email"
                        required
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.sender}
                        onChange={e => setFormData({ ...formData, sender: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Subject</label>
                    <input
                        type="text"
                        required
                        placeholder="e.g., Login pages are crashing"
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.subject}
                        onChange={e => setFormData({ ...formData, subject: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Content (Body)</label>
                    <textarea
                        required
                        placeholder="Describe the issue..."
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        rows="6"
                        value={formData.content}
                        onChange={e => setFormData({ ...formData, content: e.target.value })}
                    />
                </div>
                <div className="flex justify-end pt-4">
                    <button type="submit" className="btn-primary flex items-center gap-2">
                        <span className="w-4 h-4">📧</span>
                        <span>Send Mock Email</span>
                    </button>
                </div>
            </form>
        </Modal>
    );
}

export function AssignAgentModal({ isOpen, onClose, onAssign, currentAssignee, complaintId }) {
    const [agents, setAgents] = useState([]);
    const [selectedAgent, setSelectedAgent] = useState(currentAssignee || '');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (isOpen && complaintId) {
            fetchAgents();
        }
    }, [isOpen, complaintId]);

    const fetchAgents = async () => {
        setIsLoading(true);
        try {
            const { complaintService } = await import('../../services/complaintService');
            // Fetch agents with AI scores
            const data = await complaintService.getAssignableUsers(complaintId);
            setAgents(data);
        } catch (error) {
            console.error("Failed to fetch agents", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onAssign(selectedAgent);
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Assign Agent with AI">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                    <label className="block text-sm text-gray-400 mb-1">Select Agent</label>
                    <div className="max-h-60 overflow-y-auto space-y-2 pr-1">
                        {isLoading ? (
                            <div className="text-center text-gray-500 py-4">Analying workload & skills...</div>
                        ) : agents.length === 0 ? (
                            <div className="text-center text-gray-500 py-4">No eligible agents found</div>
                        ) : (
                            agents.map(agent => (
                                <div
                                    key={agent.user_id}
                                    onClick={() => setSelectedAgent(agent.user_id)}
                                    className={`p-3 rounded-lg border cursor-pointer transition-all flex items-center justify-between group
                                        ${selectedAgent === agent.user_id
                                            ? 'bg-primary-500/20 border-primary-500 ring-1 ring-primary-500'
                                            : 'bg-white/5 border-white/10 hover:bg-white/10'
                                        }`}
                                >
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2">
                                            <span className="font-medium text-white">{agent.name}</span>
                                            {agent.is_recommended && (
                                                <span className="flex items-center gap-1 px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                                                    <Sparkles className="w-3 h-3" /> AI Suggested
                                                </span>
                                            )}
                                        </div>
                                        <div className="text-xs text-gray-400 mt-1 flex items-center gap-2">
                                            <span>{agent.role}</span>
                                            <span>•</span>
                                            <span>Score: {agent.match_score > 0 ? agent.match_score.toFixed(0) : 'N/A'}</span>
                                            {agent.workload_current !== undefined && (
                                                <>
                                                    <span>•</span>
                                                    <span className={agent.workload_current > 5 ? 'text-amber-400' : 'text-slate-400'}>
                                                        Workload: {agent.workload_current}
                                                    </span>
                                                </>
                                            )}
                                        </div>
                                        {agent.recommendation_reason && (
                                            <div className="text-[10px] text-primary-300 mt-1">
                                                {agent.recommendation_reason}
                                            </div>
                                        )}
                                    </div>
                                    <div className={`w-4 h-4 rounded-full border flex items-center justify-center
                                        ${selectedAgent === agent.user_id
                                            ? 'border-primary-500 bg-primary-500'
                                            : 'border-gray-500'
                                        }`}>
                                        {selectedAgent === agent.user_id && <div className="w-2 h-2 rounded-full bg-white" />}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
                <div className="flex justify-end pt-4">
                    <button
                        type="submit"
                        disabled={!selectedAgent || isLoading}
                        className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Save className="w-4 h-4" />
                        <span>Confirm Assignment</span>
                    </button>
                </div>
            </form>
        </Modal>
    );
}

export function CreateUserModal({ isOpen, onClose, onCreate, initialData = null, isEdit = false }) {
    const [departments, setDepartments] = useState([]);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        role: 'AGENT',
        department_id: '',
        team: ''
    });

    useEffect(() => {
        if (isOpen) {
            fetchDepartments();
            if (isEdit && initialData) {
                setFormData({
                    name: initialData.name || '',
                    email: initialData.email || '',
                    password: '', // Keep empty for security, only update if changed
                    role: initialData.role || 'AGENT',
                    department_id: initialData.department_id || '',
                    team: initialData.team || ''
                });
            } else {
                // Reset form for create mode
                setFormData({
                    name: '',
                    email: '',
                    password: '',
                    role: 'AGENT',
                    department_id: '',
                    team: ''
                });
            }
        }
    }, [isOpen, initialData, isEdit]);

    const fetchDepartments = async () => {
        try {
            const { authService } = await import('../../services/authService');
            const { departmentService } = await import('../../services/departmentService');
            const org = await authService.getDefaultOrg();
            const depts = await departmentService.getAll(org.org_id);
            setDepartments(depts);
        } catch (error) {
            console.error("Failed to fetch departments", error);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        // For edit, remove password if empty
        const submissionData = { ...formData };
        if (isEdit && !submissionData.password) {
            delete submissionData.password;
        }
        onCreate(submissionData);
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={isEdit ? "Edit User" : "Create New User"}>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Full Name</label>
                    <input
                        type="text"
                        required
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.name}
                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Email</label>
                    <input
                        type="email"
                        required
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.email}
                        onChange={e => setFormData({ ...formData, email: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">
                        Password {isEdit && <span className="text-xs text-gray-500">(Leave blank to keep unchanged)</span>}
                    </label>
                    <input
                        type="password"
                        required={!isEdit}
                        minLength={8}
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.password}
                        onChange={e => setFormData({ ...formData, password: e.target.value })}
                    />
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Role</label>
                        <select
                            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors uppercase"
                            value={formData.role}
                            onChange={e => setFormData({ ...formData, role: e.target.value })}
                        >
                            <option value="AGENT">Agent</option>
                            <option value="MANAGER">Manager</option>
                            <option value="ADMIN">Admin</option>
                            <option value="VIEWER">Viewer</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Department</label>
                        <select
                            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                            value={formData.department_id}
                            onChange={e => setFormData({ ...formData, department_id: e.target.value })}
                        >
                            <option value="">Select Department</option>
                            {departments.map(dept => (
                                <option key={dept.department_id} value={dept.department_id}>{dept.name}</option>
                            ))}
                        </select>
                    </div>
                </div>
                <div>
                    <label className="block text-sm text-gray-400 mb-1">Team (Optional)</label>
                    <input
                        type="text"
                        placeholder="e.g. Frontend, DevOps"
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.team}
                        onChange={e => setFormData({ ...formData, team: e.target.value })}
                    />
                </div>
                <div className="flex justify-end pt-4">
                    <button type="submit" className="btn-primary flex items-center gap-2">
                        <Save className="w-4 h-4" />
                        <span>{isEdit ? "Update User" : "Create User"}</span>
                    </button>
                </div>
            </form>
        </Modal>
    );
}

