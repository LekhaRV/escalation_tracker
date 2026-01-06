import { useState, useEffect } from 'react';
import { X, Save, Sparkles } from 'lucide-react';

export function Modal({ isOpen, onClose, title, children }) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
            <div className="relative bg-white border border-slate-200 rounded-xl shadow-2xl w-full max-w-lg overflow-hidden animate-scale-in">
                <div className="flex items-center justify-between p-4 border-b border-slate-100">
                    <h2 className="text-lg font-bold text-slate-900">{title}</h2>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-900 transition-colors">
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

export function ConfirmationModal({ isOpen, onClose, onConfirm, title, message, confirmText = "Confirm", cancelText = "Cancel", isDangerous = false }) {
    return (
        <Modal isOpen={isOpen} onClose={onClose} title={title}>
            <div className="space-y-4">
                <p className="text-slate-600">{message}</p>
                <div className="flex justify-end gap-3 pt-2">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-white border border-slate-200 rounded-lg text-slate-700 hover:bg-slate-50 transition-colors text-sm font-medium"
                    >
                        {cancelText}
                    </button>
                    <button
                        onClick={() => { onConfirm(); onClose(); }}
                        className={`px-4 py-2 rounded-lg text-white text-sm font-medium transition-colors ${isDangerous ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'}`}
                    >
                        {confirmText}
                    </button>
                </div>
            </div>
        </Modal>
    );
}

export function ProjectModal({ isOpen, onClose, onSubmit, initialData = null, isEdit = false }) {
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
            if (isEdit && initialData) {
                setFormData({
                    project_name: initialData.project_name || '',
                    project_code: initialData.project_code || '',
                    client_name: initialData.client_name || '',
                    description: initialData.description || '',
                    department_id: initialData.department_id || ''
                });
            } else {
                setFormData({
                    project_name: '',
                    project_code: '',
                    client_name: '',
                    description: '',
                    department_id: ''
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
        onSubmit(formData);
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={isEdit ? "Edit Project" : "Create New Project"}>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm text-slate-500 mb-1">Project Name</label>
                    <input
                        type="text"
                        required
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
                        value={formData.project_name}
                        onChange={e => setFormData({ ...formData, project_name: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-slate-500 mb-1">Project Code</label>
                    <input
                        type="text"
                        required
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
                        value={formData.project_code}
                        onChange={e => setFormData({ ...formData, project_code: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-slate-500 mb-1">Department</label>
                    <select
                        required
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
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
                    <label className="block text-sm text-slate-500 mb-1">Client Name</label>
                    <input
                        type="text"
                        required
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
                        value={formData.client_name}
                        onChange={e => setFormData({ ...formData, client_name: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-slate-500 mb-1">Description</label>
                    <textarea
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
                        rows="3"
                        value={formData.description}
                        onChange={e => setFormData({ ...formData, description: e.target.value })}
                    />
                </div>
                <div className="flex justify-end pt-4">
                    <button type="submit" className="btn-primary flex items-center gap-2">
                        <Save className="w-4 h-4" />
                        <span>{isEdit ? "Update Project" : "Create Project"}</span>
                    </button>
                </div>
            </form>
        </Modal>
    );
}

export function TeamMemberModal({ isOpen, onClose, onSubmit, departmentId, initialData = null, isEdit = false }) {
    const [users, setUsers] = useState([]);
    const [formData, setFormData] = useState({
        user_id: '',
        role: 'Developer',
        specialization: ''
    });

    useEffect(() => {
        if (isOpen) {
            if (departmentId) fetchUsers();

            if (isEdit && initialData) {
                setFormData({
                    user_id: initialData.user_id,
                    role: initialData.role,
                    // Handle array or string for specialization
                    specialization: Array.isArray(initialData.specialization)
                        ? initialData.specialization.join(', ')
                        : (initialData.specialization || '')
                });
            } else {
                setFormData({
                    user_id: '',
                    role: 'Developer',
                    specialization: ''
                });
            }
        }
    }, [isOpen, departmentId, initialData, isEdit]);

    const fetchUsers = async () => {
        try {
            const { userService } = await import('../../services/userService');
            const data = await userService.getUsers();
            const deptUsers = data.items.filter(u => u.department_id === departmentId && u.role !== 'VIEWER');
            setUsers(deptUsers);
        } catch (error) {
            console.error("Failed to fetch users", error);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit({
            ...formData,
            specialization: formData.specialization.split(',').map(s => s.trim())
        });
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={isEdit ? "Update Team Member" : "Add Team Member"}>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm text-slate-500 mb-1">Select User</label>
                    <select
                        required
                        disabled={isEdit} // Cannot change user in edit mode, only role
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                        value={formData.user_id}
                        onChange={e => setFormData({ ...formData, user_id: e.target.value })}
                    >
                        <option value="">Select User</option>
                        {users.map(u => (
                            <option key={u.user_id} value={u.user_id}>{u.name} ({u.email})</option>
                        ))}
                        {/* If editing and user list doesn't have the user (e.g. diff dept), manually add option? 
                            Ideally fetchUsers gets all. For now assuming fetched. 
                        */}
                    </select>
                </div>
                <div>
                    <label className="block text-sm text-slate-500 mb-1">Role</label>
                    <select
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
                        value={formData.role}
                        onChange={e => setFormData({ ...formData, role: e.target.value })}
                    >
                        <option value="Developer">Developer</option>
                        <option value="Tester">Tester</option>
                        <option value="DevOps">DevOps</option>
                        <option value="Designer">Designer</option>
                        <option value="Manager">Manager</option>
                        <option value="Lead">Lead</option>
                        <option value="Architect">Architect</option>
                    </select>
                </div>
                <div>
                    <label className="block text-sm text-slate-500 mb-1">Specialization (comma separated)</label>
                    <input
                        type="text"
                        placeholder="React, Python, AWS"
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
                        value={formData.specialization}
                        onChange={e => setFormData({ ...formData, specialization: e.target.value })}
                    />
                </div>
                <div className="flex justify-end pt-4">
                    <button type="submit" className="btn-primary flex items-center gap-2">
                        <Save className="w-4 h-4" />
                        <span>{isEdit ? "Update Member" : "Add Member"}</span>
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
                    <label className="block text-sm text-slate-500 mb-1">Subject</label>
                    <input
                        type="text"
                        required
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
                        value={formData.subject}
                        onChange={e => setFormData({ ...formData, subject: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-slate-500 mb-1">Description</label>
                    <textarea
                        required
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
                        rows="4"
                        value={formData.description}
                        onChange={e => setFormData({ ...formData, description: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-slate-500 mb-1">Customer Name</label>
                    <input
                        type="text"
                        required
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
                        value={formData.customer_name}
                        onChange={e => setFormData({ ...formData, customer_name: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-slate-500 mb-1">Customer Email</label>
                    <input
                        type="email"
                        required
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
                        value={formData.customer_email}
                        onChange={e => setFormData({ ...formData, customer_email: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-slate-500 mb-1">Priority</label>
                    <select
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
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
                    <label className="block text-sm text-slate-500 mb-1">Project</label>
                    <select
                        required
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
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
            <div className="mb-4 p-3 bg-blue-50 border border-blue-100 rounded-lg text-sm text-blue-700">
                This tool sends a fake email to the backend to test the AI processing pipeline without needing a real SMTP connection.
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm text-slate-500 mb-1">From (Sender Email)</label>
                    <input
                        type="email"
                        required
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
                        value={formData.sender}
                        onChange={e => setFormData({ ...formData, sender: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-slate-500 mb-1">Subject</label>
                    <input
                        type="text"
                        required
                        placeholder="e.g., Login pages are crashing"
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
                        value={formData.subject}
                        onChange={e => setFormData({ ...formData, subject: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-slate-500 mb-1">Content (Body)</label>
                    <textarea
                        required
                        placeholder="Describe the issue..."
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
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
                    <label className="block text-sm text-slate-500 mb-1">Select Agent</label>
                    <div className="max-h-60 overflow-y-auto space-y-2 pr-1">
                        {isLoading ? (
                            <div className="text-center text-slate-500 py-4">Analying workload & skills...</div>
                        ) : agents.length === 0 ? (
                            <div className="text-center text-slate-500 py-4">No eligible agents found</div>
                        ) : (
                            agents.map(agent => (
                                <div
                                    key={agent.user_id}
                                    onClick={() => setSelectedAgent(agent.user_id)}
                                    className={`p-3 rounded-lg border cursor-pointer transition-all flex items-center justify-between group
                                        ${selectedAgent === agent.user_id
                                            ? 'bg-blue-50 border-blue-500 ring-1 ring-blue-500'
                                            : 'bg-white border-slate-200 hover:bg-slate-50'
                                        }`}
                                >
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2">
                                            <span className="font-medium text-slate-900">{agent.name}</span>
                                            {agent.is_recommended && (
                                                <span className="flex items-center gap-1 px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-emerald-50 text-emerald-600 border border-emerald-200">
                                                    <Sparkles className="w-3 h-3" /> AI Suggested
                                                </span>
                                            )}
                                        </div>
                                        <div className="text-xs text-slate-500 mt-1 flex items-center gap-2">
                                            <span>{agent.role}</span>
                                            <span>•</span>
                                            <span>Score: {agent.match_score > 0 ? agent.match_score.toFixed(0) : 'N/A'}</span>
                                            {agent.workload_current !== undefined && (
                                                <>
                                                    <span>•</span>
                                                    <span className={agent.workload_current > 5 ? 'text-amber-600' : 'text-slate-500'}>
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
                                            ? 'border-blue-500 bg-blue-500'
                                            : 'border-slate-300'
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
        role: 'agent',
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
                    role: initialData.role || 'agent',
                    department_id: initialData.department_id || '',
                    team: initialData.team || ''
                });
            } else {
                // Reset form for create mode
                setFormData({
                    name: '',
                    email: '',
                    password: '',
                    role: 'agent',
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
        console.log('Submitting User Form (New Code Loaded) - Role:', formData.role);
        // For edit, remove password if empty
        const submissionData = { ...formData };
        if (isEdit && !submissionData.password) {
            delete submissionData.password;
        }

        // Convert empty string to null for optional UUID fields
        if (submissionData.department_id === '') {
            submissionData.department_id = null;
        }
        if (submissionData.team === '') {
            submissionData.team = null;
        }

        onCreate(submissionData);
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={isEdit ? "Edit User" : "Create New User"}>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm text-slate-500 mb-1">Full Name</label>
                    <input
                        type="text"
                        required
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
                        value={formData.name}
                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-slate-500 mb-1">Email</label>
                    <input
                        type="email"
                        required
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
                        value={formData.email}
                        onChange={e => setFormData({ ...formData, email: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm text-slate-500 mb-1">
                        Password {isEdit && <span className="text-xs text-slate-400">(Leave blank to keep unchanged)</span>}
                    </label>
                    <input
                        type="password"
                        required={!isEdit}
                        minLength={8}
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
                        value={formData.password}
                        onChange={e => setFormData({ ...formData, password: e.target.value })}
                    />
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm text-slate-500 mb-1">Role</label>
                        <select
                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors uppercase"
                            value={formData.role}
                            onChange={e => setFormData({ ...formData, role: e.target.value })}
                        >
                            <option value="agent">Agent</option>
                            <option value="manager">Manager</option>
                            <option value="admin">Admin</option>
                            <option value="viewer">Viewer</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm text-slate-500 mb-1">Department</label>
                        <select
                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
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
                    <label className="block text-sm text-slate-500 mb-1">Team (Optional)</label>
                    <input
                        type="text"
                        placeholder="e.g. Frontend, DevOps"
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:border-blue-500 outline-none transition-colors"
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

