import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { AlertCircle, ArrowRight, Loader } from 'lucide-react';

function Login() {
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        name: '',
        orgName: ''
    });

    const { login, register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            if (isLogin) {
                await login(formData.email, formData.password);
            } else {
                await register(formData.email, formData.password, formData.name, formData.orgName);
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
        <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-[#0f172a]">
            {/* Background decorations */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/20 rounded-full blur-[128px]" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-500/20 rounded-full blur-[128px]" />
            </div>

            <div className="w-full max-w-md relative z-10 glass rounded-2xl p-8 shadow-2xl shadow-primary-500/10 border border-white/5">
                <div className="flex flex-col items-center mb-8">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center mb-4 shadow-lg shadow-primary-500/25">
                        <AlertCircle className="w-7 h-7 text-white" />
                    </div>
                    <h1 className="text-2xl font-bold text-white tracking-tight">
                        {isLogin ? 'Welcome back' : 'Create account'}
                    </h1>
                    <p className="text-gray-400 mt-2 text-sm text-center">
                        {isLogin
                            ? 'Enter your credentials to access the Tarento complaint tracker'
                            : 'Join your team and start managing complaints effectively'}
                    </p>
                </div>

                {error && (
                    <div className="mb-6 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm flex items-center gap-2">
                        <AlertCircle className="w-4 h-4" />
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    {!isLogin && (
                        <>
                            <div>
                                <label className="block text-xs font-medium text-gray-400 mb-1 ml-1" htmlFor="name">
                                    FULL NAME
                                </label>
                                <input
                                    id="name"
                                    name="name"
                                    type="text"
                                    required
                                    value={formData.name}
                                    onChange={handleChange}
                                    className="input"
                                    placeholder="John Doe"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-medium text-gray-400 mb-1 ml-1" htmlFor="orgName">
                                    ORGANIZATION NAME (Optional)
                                </label>
                                <input
                                    id="orgName"
                                    name="orgName"
                                    type="text"
                                    value={formData.orgName}
                                    onChange={handleChange}
                                    className="input"
                                    placeholder="Leave empty to join existing"
                                />
                            </div>
                        </>
                    )}

                    <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1 ml-1" htmlFor="email">
                            EMAIL ADDRESS
                        </label>
                        <input
                            id="email"
                            name="email"
                            type="email"
                            required
                            value={formData.email}
                            onChange={handleChange}
                            className="input"
                            placeholder="name@tarento.com"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1 ml-1" htmlFor="password">
                            PASSWORD
                        </label>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            required
                            value={formData.password}
                            onChange={handleChange}
                            className="input"
                            placeholder="••••••••"
                        />
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
                        }}
                        className="text-sm text-gray-400 hover:text-white transition-colors"
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
