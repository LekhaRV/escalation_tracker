import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Save } from 'lucide-react';
import { authService } from '../services/authService';

function Settings() {
    const { user } = useAuth();
    const [formData, setFormData] = useState({
        name: user?.name,
        email: user?.email,
        current_password: '',
        new_password: ''
    });
    const [status, setStatus] = useState('');

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await authService.updateProfile(formData);
            setStatus('Profile updated successfully');
            setFormData({ ...formData, current_password: '', new_password: '' });
        } catch (error) {
            setStatus('Update failed: ' + (error.response?.data?.detail || 'Unknown error'));
        }
    };

    return (
        <div className="max-w-2xl mx-auto animate-fade-in">
            <h1 className="text-2xl font-bold text-slate-900 mb-6">Settings</h1>

            <div className="card bg-white border border-slate-200 shadow-sm rounded-xl p-8">
                <form onSubmit={handleSubmit} className="space-y-6">
                    <h2 className="text-lg font-bold text-slate-800 border-b border-slate-100 pb-2">Profile</h2>

                    <div>
                        <label className="block text-sm font-semibold text-slate-600 mb-1">Full Name</label>
                        <input
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            className="input"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-slate-600 mb-1">Email</label>
                        <input
                            name="email"
                            value={formData.email}
                            disabled
                            className="input opacity-70 bg-slate-50 cursor-not-allowed text-slate-500"
                        />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-semibold text-slate-600 mb-1">Role</label>
                            <input
                                value={user?.role || ''}
                                disabled
                                className="input opacity-70 bg-slate-50 cursor-not-allowed uppercase text-slate-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-slate-600 mb-1">Department</label>
                            <input
                                value={user?.department_name || 'N/A'}
                                disabled
                                className="input opacity-70 bg-slate-50 cursor-not-allowed text-slate-500"
                            />
                        </div>
                    </div>

                    <h2 className="text-lg font-bold text-slate-800 border-b border-slate-100 pb-2 pt-4">Security</h2>

                    <div>
                        <label className="block text-sm font-semibold text-slate-600 mb-1">Current Password</label>
                        <input
                            name="current_password"
                            type="password"
                            value={formData.current_password}
                            onChange={handleChange}
                            className="input"
                            placeholder="Required to change password"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-slate-600 mb-1">New Password</label>
                        <input
                            name="new_password"
                            type="password"
                            value={formData.new_password}
                            onChange={handleChange}
                            className="input"
                            placeholder="Leave empty to keep current"
                        />
                    </div>

                    <div className="pt-4 border-t border-slate-100 mt-6">
                        <button type="submit" className="btn-primary flex items-center gap-2">
                            <Save className="w-4 h-4" /> Save Changes
                        </button>
                        {status && (
                            <p className={`mt-3 text-sm font-medium ${status.includes('failed') ? 'text-red-600' : 'text-emerald-600'}`}>
                                {status}
                            </p>
                        )}
                    </div>
                </form>
            </div>
        </div>
    );
}

export default Settings;
