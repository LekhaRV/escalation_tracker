import { useState } from 'react';
import { X, Save } from 'lucide-react';

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
    const [formData, setFormData] = useState({
        project_name: '',
        project_code: '',
        client_name: '',
        description: ''
    });

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

export function AddMemberModal({ isOpen, onClose, onAdd }) {
    const [formData, setFormData] = useState({
        user_email: '',
        role: 'Developer',
        specialization: ''
    });

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
                    <label className="block text-sm text-gray-400 mb-1">User Email</label>
                    <input
                        type="email"
                        required
                        placeholder="dev@tarento.com"
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none transition-colors"
                        value={formData.user_email}
                        onChange={e => setFormData({ ...formData, user_email: e.target.value })}
                    />
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
    const [formData, setFormData] = useState({
        subject: '',
        description: '',
        customer_name: '',
        customer_email: '',
        priority: 'medium'
    });

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
                <div className="flex justify-end pt-4">
                    <button type="submit" className="btn-primary flex items-center gap-2">
                        <Save className="w-4 h-4" />
                        <span>Create Complaint</span>
                    </button>
                </div>
            </form>
        </Modal>
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
