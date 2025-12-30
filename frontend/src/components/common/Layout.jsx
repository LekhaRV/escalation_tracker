import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';

function Layout() {
    return (
        <div className="min-h-screen bg-[#0f172a]">
            <Sidebar />
            <Navbar />
            <main className="pl-64 pt-16 min-h-screen">
                <div className="p-8 max-w-7xl mx-auto">
                    <Outlet />
                </div>
            </main>
        </div>
    );
}

export default Layout;
