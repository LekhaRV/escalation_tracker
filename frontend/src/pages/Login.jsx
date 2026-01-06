import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowRight, Loader, Lock, Sparkles } from 'lucide-react';

function Login() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });

    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            await login(formData.email, formData.password);
            navigate('/');
        } catch (err) {
            setError(err.response?.data?.detail || 'Invalid credentials. Please contact your administrator.');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    return (
        <div className="min-h-screen flex w-full relative overflow-hidden bg-app">
            {/* Left Side - Brand (Sapphire Blue) */}
            <div className="hidden lg:flex w-1/2 relative z-10 flex-col justify-between p-12 bg-brand-700 text-white">
                <div>
                    <div className="flex items-center gap-3">
                        <img src="/traxion_logo_1.jpg" alt="Traxion" className="w-10 h-10 object-contain rounded" />
                        <h1 className="text-2xl font-bold tracking-tight">Traxion</h1>
                    </div>
                </div>

                <div className="relative">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 border border-white/20 text-brand-100 text-xs font-semibold mb-6">
                        <Sparkles className="w-3 h-3 text-accent" />
                        <span>AI-Powered Platform</span>
                    </div>
                    <h2 className="text-5xl font-bold mb-6 leading-tight text-white">
                        Intelligent Resolution <br />
                        <span className="text-accent">Simplified.</span>
                    </h2>
                    <p className="text-lg text-brand-100 max-w-md leading-relaxed">
                        Streamline your operations with predictive insights and automated routing.
                        The smarter way to manage escalations.
                    </p>
                </div>

                {/* Decorative Circles */}
                <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 w-96 h-96 bg-white/5 rounded-full blur-3xl pointer-events-none" />
                <div className="absolute bottom-0 left-0 translate-y-1/2 -translate-x-1/2 w-96 h-96 bg-accent/20 rounded-full blur-3xl pointer-events-none" />
            </div>

            {/* Right Side - Login Form (Light Mode) */}
            <div className="w-full lg:w-1/2 flex items-center justify-center p-8 relative bg-surface">
                <div className="w-full max-w-md relative z-10">
                    <div className="mb-10 text-center lg:text-left">
                        <div className="lg:hidden flex justify-center mb-6">
                            <img src="/traxion_logo.png" alt="Traxion" className="w-16 h-16 object-contain" />
                        </div>
                        <h2 className="text-3xl font-bold text-logic mb-2">Welcome Back</h2>
                        <p className="text-algo">Please sign in to your workspace</p>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm flex items-center gap-3">
                            <div className="w-1 h-8 bg-red-500 rounded-full"></div>
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-muted ml-1" htmlFor="email">
                                Work Email
                            </label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                required
                                value={formData.email}
                                onChange={handleChange}
                                className="input"
                                placeholder="name@company.com"
                            />
                        </div>

                        <div className="space-y-2">
                            <div className="flex items-center justify-between">
                                <label className="text-xs font-semibold text-muted ml-1" htmlFor="password">
                                    Password
                                </label>
                            </div>
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
                            className="w-full bg-brand-700 hover:bg-brand-800 text-white font-semibold py-4 rounded-xl transition-all duration-200 shadow-lg shadow-brand-700/20 flex items-center justify-center gap-2 group mt-8"
                        >
                            {loading ? (
                                <Loader className="w-5 h-5 animate-spin" />
                            ) : (
                                <>
                                    Sign In
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-8 pt-8 border-t border-slate-100 text-center">
                        <p className="text-sm text-muted flex items-center justify-center gap-2">
                            <Lock className="w-3 h-3" />
                            Secure Enterprise Access
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Login;
