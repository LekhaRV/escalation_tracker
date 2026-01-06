import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

function Layout() {
    return (
        <div className="min-h-screen bg-app">
            <Sidebar />
            <main className="pl-64 min-h-screen transition-all duration-300">
                <div className="p-6 mx-auto w-full animate-fade-in">
                    <Outlet />
                </div>
            </main>
        </div>
    );
}

export default Layout;
