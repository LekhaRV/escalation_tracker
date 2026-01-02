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
        { name: 'Escalations', href: '/complaints', icon: MessageSquare },
        { name: 'Projects', href: '/projects', icon: Briefcase },
    ];

    // Add Admin links
    if (['admin', 'ADMIN'].includes(user?.role)) {
        navigation.push({ name: 'Users', href: '/users', icon: Users });
        navigation.push({ name: 'Settings', href: '/settings', icon: Settings });
    }

    const isActive = (path) => location.pathname === path;

    return (
        <div className="flex flex-col w-64 bg-slate-100 border-r border-slate-200 h-screen fixed left-0 top-0 z-50 transition-colors">
            {/* Logo */}
            <div className="flex items-center gap-3 px-6 h-16 border-b border-slate-200">
                <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-sm">
                    <AlertCircle className="w-5 h-5 text-white" />
                </div>
                <div>
                    <h1 className="text-slate-900 font-bold tracking-tight">Escalation Manager</h1>
                    <p className="text-xs text-slate-500">Complaint Tracker</p>
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
                                ? 'bg-blue-50 text-blue-700'
                                : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'
                                }`}
                        >
                            <item.icon className={`w-5 h-5 transition-colors ${active ? 'text-blue-600' : 'text-slate-400 group-hover:text-slate-600'
                                }`} />
                            <span className="font-medium">{item.name}</span>
                            {active && (
                                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-blue-600" />
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* User & Logout */}
            <div className="p-4 border-t border-slate-200">
                <div className="flex items-center gap-3 px-3 py-3 rounded-lg bg-slate-50 mb-3 border border-slate-100">
                    <div className="w-9 h-9 rounded-full bg-slate-200 flex items-center justify-center text-sm font-bold text-slate-700">
                        {user?.name?.charAt(0) || 'U'}
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <p className="text-sm font-medium text-slate-900 truncate">{user?.name}</p>
                        <p className="text-xs text-slate-500 truncate capitalize">{user?.role?.replace('_', ' ')}</p>
                    </div>
                </div>

                <button
                    onClick={logout}
                    className="w-full flex items-center gap-3 px-3 py-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors group"
                >
                    <LogOut className="w-5 h-5 group-hover:text-red-500 transition-colors" />
                    <span className="font-medium">Sign Out</span>
                </button>
            </div>
        </div>
    );
}

export default Sidebar;
