import { Link, useLocation } from 'react-router-dom';
import {
    LayoutDashboard,
    MessageSquare,
    Briefcase,
    Building2,
    BarChart2,
    Users,
    LogOut,
    AlertCircle,
    Settings,
    Shield
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

function Sidebar() {
    const location = useLocation();
    const { user, logout } = useAuth();

    const navigation = [
        { name: 'Dashboard', href: '/', icon: LayoutDashboard },
        { name: 'Complaints', href: '/complaints', icon: MessageSquare },
        { name: 'Projects', href: '/projects', icon: Briefcase },
        { name: 'Departments', href: '/departments', icon: Building2 },
    ];

    // Add Admin links
    if (['admin', 'ADMIN'].includes(user?.role)) {
        navigation.push({ name: 'Users', href: '/users', icon: Users });
        navigation.push({ name: 'Settings', href: '/settings', icon: Settings });
    }

    const isActive = (path) => location.pathname === path;

    return (
        <div className="flex flex-col w-64 bg-brand-700 border-r border-brand-800 h-screen fixed left-0 top-0 z-50 shadow-2xl">
            {/* Header */}
            <div className="flex items-center gap-3 px-6 h-20 border-b border-brand-800 bg-brand-700">
                <div className="bg-white/10 p-1.5 rounded-lg border border-white/20">
                    <img src="/traxion_logo_1.jpg" alt="Traxion" className="w-8 h-8 object-contain rounded" />
                </div>
                <div>
                    <h1 className="text-white font-bold tracking-tight text-xl">Traxion</h1>
                    <p className="text-[10px] text-brand-200 font-medium uppercase tracking-wide">Enterprise</p>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-8 space-y-1 overflow-y-auto">
                {navigation.map((item) => {
                    const active = isActive(item.href);
                    return (
                        <Link
                            key={item.name}
                            to={item.href}
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${active
                                ? 'bg-white text-brand-700 shadow-md font-bold border border-white'
                                : 'text-brand-200 hover:text-white hover:bg-brand-600'
                                }`}
                        >
                            <item.icon className={`w-5 h-5 transition-colors ${active ? 'text-accent' : 'text-brand-300 group-hover:text-white'
                                }`} />
                            <span className="text-sm">{item.name}</span>
                        </Link>
                    );
                })}
            </nav>

            {/* User & Logout */}
            <div className="p-4 border-t border-brand-800 bg-brand-700">
                <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 flex items-center justify-center rounded-full bg-brand-600 text-white font-bold shadow-sm border border-brand-500">
                        {user?.name?.charAt(0) || 'U'}
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <p className="text-sm font-bold text-white truncate">{user?.name}</p>
                        <p className="text-xs text-brand-200 truncate capitalize">{user?.role?.replace('_', ' ')}</p>
                    </div>
                </div>

                <button
                    onClick={logout}
                    className="w-full flex items-center justify-center gap-2 px-3 py-2 text-brand-200 hover:text-white hover:bg-brand-600 rounded-lg transition-colors group"
                >
                    <LogOut className="w-4 h-4" />
                    <span className="font-medium text-xs uppercase tracking-wider">Log Out</span>
                </button>
            </div>
        </div>
    );
}

export default Sidebar;
