import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Save, User, Shield, Lock, Mail, Building, Eye, EyeOff } from 'lucide-react';
import { authService } from '../services/authService';

function Settings() {
    const { user } = useAuth();
    const [formData, setFormData] = useState({
        name: user?.name || '',
        email: user?.email || '',
        current_password: '',
        new_password: ''
    });
    const [status, setStatus] = useState({ type: '', message: '' });
    const [showNewPassword, setShowNewPassword] = useState(false);
    const [showCurrentPassword, setShowCurrentPassword] = useState(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        if (status.message) setStatus({ type: '', message: '' });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await authService.updateProfile(formData);
            setStatus({ type: 'success', message: 'Profile updated successfully' });
            setFormData(prev => ({ ...prev, current_password: '', new_password: '' }));
        } catch (error) {
            setStatus({ type: 'error', message: 'Update failed: ' + (error.response?.data?.detail || 'Unknown error') });
        }
    };

    return (
        <div className="max-w-4xl mx-auto animate-fade-in space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Account Settings</h1>
                    <p className="text-slate-500 text-sm mt-1">Manage your profile and security preferences</p>
                </div>
            </div>

            <form onSubmit={handleSubmit}>
                <div className="bg-white border border-slate-200 rounded-xl shadow-sm divide-y divide-slate-100 overflow-hidden">

                    {/* Profile Section */}
                    <div className="p-6">
                        <div className="flex items-center gap-2 mb-6 text-slate-900 font-semibold text-lg">
                            <User className="w-5 h-5 text-blue-500" />
                            <h2>Profile Information</h2>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-xs font-semibold text-slate-500 uppercase mb-2">Full Name</label>
                                <div className="relative">
                                    <input
                                        name="name"
                                        value={formData.name}
                                        onChange={handleChange}
                                        className="input pl-10 bg-slate-50 border-slate-200 text-slate-900 focus:border-blue-500"
                                        placeholder="Your full name"
                                    />
                                    <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                                </div>
                            </div>

                            <div>
                                <label className="block text-xs font-semibold text-slate-500 uppercase mb-2">Email Address</label>
                                <div className="relative">
                                    <input
                                        name="email"
                                        value={formData.email}
                                        disabled
                                        className="input pl-10 bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed"
                                    />
                                    <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                                </div>
                                <p className="text-xs text-slate-400 mt-1">Email cannot be changed contact admin.</p>
                            </div>

                            <div>
                                <label className="block text-xs font-semibold text-slate-500 uppercase mb-2">Role</label>
                                <div className="relative">
                                    <input
                                        value={user?.role || ''}
                                        disabled
                                        className="input pl-10 bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed uppercase"
                                    />
                                    <Shield className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                                </div>
                            </div>

                            <div>
                                <label className="block text-xs font-semibold text-slate-500 uppercase mb-2">Department</label>
                                <div className="relative">
                                    <input
                                        value={user?.department_name || 'N/A'}
                                        disabled
                                        className="input pl-10 bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed"
                                    />
                                    <Building className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Security Section */}
                    <div className="p-6 bg-slate-50/50">
                        <div className="flex items-center gap-2 mb-6 text-slate-900 font-semibold text-lg">
                            <Lock className="w-5 h-5 text-blue-500" />
                            <h2>Security</h2>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-xs font-semibold text-slate-500 uppercase mb-2">New Password</label>
                                <div className="relative">
                                    <input
                                        name="new_password"
                                        type={showNewPassword ? "text" : "password"}
                                        value={formData.new_password}
                                        onChange={handleChange}
                                        className="input bg-white border-slate-200 text-slate-900 focus:border-blue-500 pr-10"
                                        placeholder="Leave empty to keep current"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowNewPassword(!showNewPassword)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                                    >
                                        {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                    </button>
                                </div>
                            </div>
                            <div>
                                <label className="block text-xs font-semibold text-slate-500 uppercase mb-2">Current Password</label>
                                <div className="relative">
                                    <input
                                        name="current_password"
                                        type={showCurrentPassword ? "text" : "password"}
                                        value={formData.current_password}
                                        onChange={handleChange}
                                        className="input bg-white border-slate-200 text-slate-900 focus:border-blue-500 pr-10"
                                        placeholder="Required to change password"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                                    >
                                        {showCurrentPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Action Footer */}
                    <div className="p-6 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
                        <div>
                            {status.message && (
                                <span className={`text-sm ${status.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>
                                    {status.message}
                                </span>
                            )}
                        </div>
                        <button type="submit" className="btn-primary flex items-center gap-2 px-6">
                            <Save className="w-4 h-4" /> Save Changes
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
}

export default Settings;
