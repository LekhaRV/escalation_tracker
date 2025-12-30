import { Bell, Search, Menu } from 'lucide-react';
import { useState } from 'react';

function Navbar() {
    const [hasNotifications, setHasNotifications] = useState(true);

    return (
        <header className="h-16 glass-dark border-b border-white/5 fixed top-0 right-0 left-64 z-40 bg-opacity-80 backdrop-blur-md">
            <div className="flex items-center justify-between h-full px-8">
                {/* Search */}
                <div className="flex items-center flex-1 max-w-lg">
                    <div className="relative w-full group">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 group-focus-within:text-primary-400 transition-colors" />
                        <input
                            type="text"
                            placeholder="Search complaints, projects, or people..."
                            className="w-full bg-gray-900/50 border border-white/5 rounded-full pl-10 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary-500/50 focus:ring-1 focus:ring-primary-500/50 transition-all"
                        />
                    </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-4 ml-4">
                    <button className="relative p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-full transition-colors">
                        <Bell className="w-5 h-5" />
                        {hasNotifications && (
                            <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-[#0f172a]"></span>
                        )}
                    </button>
                </div>
            </div>
        </header>
    );
}

export default Navbar;
