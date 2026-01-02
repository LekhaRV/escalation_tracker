import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { departmentService } from '../services/departmentService';
import { authService } from '../services/authService';
import { AlertCircle, ArrowRight, Loader, Eye, EyeOff } from 'lucide-react';

function Login() {
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [departments, setDepartments] = useState([]);
    const [defaultOrgId, setDefaultOrgId] = useState(null);
    const [showPassword, setShowPassword] = useState(false);
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        name: '',
        orgName: '',
        departmentId: ''
    });

    const { login, register } = useAuth();
    const navigate = useNavigate();

    // Fetch default org and departments on mount
    useEffect(() => {
        const fetchDefaults = async () => {
            try {
                const org = await authService.getDefaultOrg();
                setDefaultOrgId(org.org_id);
                const depts = await departmentService.getAll(org.org_id);
                setDepartments(depts);
            } catch (err) {
                console.error("Failed to fetch defaults:", err);
            }
        };
        fetchDefaults();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            if (isLogin) {
                await login(formData.email, formData.password);
            } else {
                await register(
                    formData.email,
                    formData.password,
                    formData.name,
                    formData.orgName,
                    formData.departmentId
                );
            }
            navigate('/');
        } catch (err) {
            setError(err.response?.data?.detail || 'An error occurred. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-slate-50">
            {/* Background decorations */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-100 rounded-full blur-[128px]" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-100 rounded-full blur-[128px]" />
            </div>

            <div className="w-full max-w-md relative z-10 bg-white/80 backdrop-blur-md rounded-2xl p-8 shadow-2xl shadow-slate-200 border border-white">
                <div className="flex flex-col items-center mb-8">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center mb-4 shadow-lg shadow-blue-500/25">
                        <AlertCircle className="w-7 h-7 text-white" />
                    </div>
                    <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                        {isLogin ? 'Welcome back' : 'Create account'}
                    </h1>
                    <p className="text-slate-500 mt-2 text-sm text-center">
                        {isLogin
                            ? 'Enter your credentials to access the Escalation Manager'
                            : 'Join your team and start managing complaints effectively'}
                    </p>
                </div>

                {error && (
                    <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm flex items-center gap-2">
                        <AlertCircle className="w-4 h-4" />
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    {!isLogin && (
                        <>
                            <div>
                                <label className="block text-xs font-medium text-slate-500 mb-1 ml-1" htmlFor="name">
                                    FULL NAME
                                </label>
                                <input
                                    id="name"
                                    name="name"
                                    type="text"
                                    required
                                    value={formData.name}
                                    onChange={handleChange}
                                    className="input bg-white border-slate-200 text-slate-900 focus:border-blue-500"
                                    placeholder="John Doe"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-medium text-slate-500 mb-1 ml-1" htmlFor="orgName">
                                    ORGANIZATION NAME (Optional)
                                </label>
                                <input
                                    id="orgName"
                                    name="orgName"
                                    type="text"
                                    value={formData.orgName}
                                    onChange={handleChange}
                                    className="input bg-white border-slate-200 text-slate-900 focus:border-blue-500"
                                    placeholder="Leave empty to join existing"
                                />
                            </div>

                            {!formData.orgName && (
                                <div>
                                    <label className="block text-xs font-medium text-slate-500 mb-1 ml-1" htmlFor="departmentId">
                                        DEPARTMENT
                                    </label>
                                    <select
                                        id="departmentId"
                                        name="departmentId"
                                        required
                                        value={formData.departmentId}
                                        onChange={handleChange}
                                        className="input bg-white border-slate-200 text-slate-900 focus:border-blue-500"
                                    >
                                        <option value="" disabled>Select Department</option>
                                        {departments.map(dept => (
                                            <option key={dept.department_id} value={dept.department_id}>
                                                {dept.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            )}
                        </>
                    )}

                    <div>
                        <label className="block text-xs font-medium text-slate-500 mb-1 ml-1" htmlFor="email">
                            EMAIL ADDRESS
                        </label>
                        <input
                            id="email"
                            name="email"
                            type="email"
                            required
                            value={formData.email}
                            onChange={handleChange}
                            className="input bg-white border-slate-200 text-slate-900 focus:border-blue-500"
                            placeholder="name@company.com"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-slate-500 mb-1 ml-1" htmlFor="password">
                            PASSWORD
                        </label>
                        <div className="relative">
                            <input
                                id="password"
                                name="password"
                                type={showPassword ? "text" : "password"}
                                required
                                value={formData.password}
                                onChange={handleChange}
                                className="input bg-white border-slate-200 text-slate-900 focus:border-blue-500 pr-10"
                                placeholder="••••••••"
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                            >
                                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                            </button>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full btn-primary py-3 mt-6 flex items-center justify-center gap-2 group"
                    >
                        {loading ? (
                            <Loader className="w-5 h-5 animate-spin" />
                        ) : (
                            <>
                                {isLogin ? 'Sign In' : 'Create Account'}
                                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </>
                        )}
                    </button>
                </form>

                <div className="mt-8 text-center">
                    <button
                        onClick={() => {
                            setIsLogin(!isLogin);
                            setError(null);
                            // Reset optional fields when switching
                            if (isLogin) {
                                setFormData(prev => ({
                                    ...prev,
                                    name: '',
                                    orgName: '',
                                    departmentId: ''
                                }));
                            }
                        }}
                        className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
                    >
                        {isLogin
                            ? "Don't have an account? Sign up"
                            : "Already have an account? Sign in"}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Login;
