import { Link, useLocation } from 'react-router-dom';
import {
    LayoutDashboard,
    MessageSquare,
    Briefcase,
    BarChart2,
    Users,
    LogOut,
    AlertCircle,
    Settings
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

function Sidebar() {
    const location = useLocation();
    const { user, logout } = useAuth();

    const navigation = [
        { name: 'Dashboard', href: '/', icon: LayoutDashboard },
        { name: 'Complaints', href: '/complaints', icon: MessageSquare },
        { name: 'Projects', href: '/projects', icon: Briefcase },
    ];

    // Add Admin links
    if (['admin', 'ADMIN'].includes(user?.role)) {
        navigation.push({ name: 'Users', href: '/users', icon: Users });
        navigation.push({ name: 'Settings', href: '/settings', icon: Settings });
    }

    const isActive = (path) => location.pathname === path;

    return (
        <div className="flex flex-col w-64 glass-dark border-r border-white/5 h-screen fixed left-0 top-0 z-50">
            {/* Logo */}
            <div className="flex items-center gap-3 px-6 h-16 border-b border-white/5">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
                    <AlertCircle className="w-5 h-5 text-white" />
                </div>
                <div>
                    <h1 className="text-white font-bold tracking-tight">Tarento API</h1>
                    <p className="text-xs text-gray-400">Complaint Tracker</p>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
                {navigation.map((item) => {
                    const active = isActive(item.href);
                    return (
                        <Link
                            key={item.name}
                            to={item.href}
                            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group ${active
                                ? 'bg-primary-500/10 text-primary-400'
                                : 'text-gray-400 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            <item.icon className={`w-5 h-5 transition-colors ${active ? 'text-primary-400' : 'text-gray-500 group-hover:text-white'
                                }`} />
                            <span className="font-medium">{item.name}</span>
                            {active && (
                                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary-400 box-shadow-glow" />
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* User & Logout */}
            <div className="p-4 border-t border-white/5">
                <div className="flex items-center gap-3 px-3 py-3 rounded-lg bg-white/5 mb-3">
                    <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-gray-700 to-gray-600 flex items-center justify-center text-sm font-bold text-white">
                        {user?.name?.charAt(0) || 'U'}
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <p className="text-sm font-medium text-white truncate">{user?.name}</p>
                        <p className="text-xs text-gray-400 truncate capitalize">{user?.role?.replace('_', ' ')}</p>
                    </div>
                </div>

                <button
                    onClick={logout}
                    className="w-full flex items-center gap-3 px-3 py-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors group"
                >
                    <LogOut className="w-5 h-5 group-hover:text-red-400 transition-colors" />
                    <span className="font-medium">Sign Out</span>
                </button>
            </div>
        </div>
    );
}

export default Sidebar;
