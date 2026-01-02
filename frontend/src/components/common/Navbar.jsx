import { Menu } from 'lucide-react';

function Navbar() {
    return (
        <header className="h-16 bg-white/80 border-b border-slate-200 fixed top-0 right-0 left-64 z-40 backdrop-blur-md transition-colors">
            <div className="flex items-center justify-between h-full px-8">
                {/* Search - Removed as per request */}
                <div className="flex items-center flex-1 max-w-lg">
                </div>

                {/* Actions */}
                <div className="flex items-center gap-4 ml-4">
                    {/* Notifications removed */}
                </div>
            </div>
        </header>
    );
}

export default Navbar;
