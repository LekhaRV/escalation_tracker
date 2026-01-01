import { Bell, Menu } from 'lucide-react';
import { useState } from 'react';

function Navbar() {
    const [hasNotifications, setHasNotifications] = useState(true);

    return (
        <header className="h-16 glass-dark border-b border-white/5 fixed top-0 right-0 left-64 z-40 bg-opacity-80 backdrop-blur-md">
            <div className="flex items-center justify-between h-full px-8">
                {/* Search - Removed as per request */}
                <div className="flex items-center flex-1 max-w-lg">
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
