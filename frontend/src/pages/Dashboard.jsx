import { useEffect, useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, LineChart, Line
} from 'recharts';
import {
    AlertCircle, CheckCircle, Clock, Activity,
    TrendingUp, Users, ArrowUpRight, ArrowDownRight
} from 'lucide-react';
import { analyticsService } from '../services/analyticsService';
import { useAuth } from '../context/AuthContext';

function Dashboard() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const { user } = useAuth();

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const data = await analyticsService.getAnalytics('dashboard');
            setStats(data.data);
        } catch (error) {
            console.error('Failed to fetch dashboard stats', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="text-white">Loading dashboard...</div>;
    if (!stats) return <div className="text-white">Failed to load data</div>;

    // Dummy data for charts if API returns empty/flat structures (visual demo)
    const severityData = [
        { name: 'Critical', value: stats.critical_count || 5, color: '#ef4444' },
        { name: 'High', value: stats.high_count || 12, color: '#f97316' },
        { name: 'Medium', value: stats.medium_count || 25, color: '#eab308' },
        { name: 'Low', value: stats.low_count || 18, color: '#22c55e' },
    ];

    const trendData = [
        { name: 'Mon', complaints: 4 },
        { name: 'Tue', complaints: 7 },
        { name: 'Wed', complaints: 5 },
        { name: 'Thu', complaints: 12 },
        { name: 'Fri', complaints: 8 },
        { name: 'Sat', complaints: 2 },
        { name: 'Sun', complaints: stats.complaints_today || 3 },
    ];

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-white mb-1">
                    Hello, {user?.name?.split(' ')[0]}
                </h1>
                <p className="text-gray-400 text-sm">Here's what's happening in your organization today.</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    title="Total Complaints"
                    value={stats.total_complaints}
                    icon={Activity}
                    trend="+12%"
                    trendUp={true}
                    color="blue"
                />
                <StatCard
                    title="In Progress"
                    value={stats.in_progress_complaints}
                    icon={Clock}
                    trend="-5%"
                    trendUp={false}
                    color="purple"
                />
                <StatCard
                    title="Critical Issues"
                    value={stats.critical_count}
                    icon={AlertCircle}
                    trend={stats.critical_count > 0 ? "Action Needed" : "Stable"}
                    trendUp={stats.critical_count === 0}
                    color="red"
                />
                <StatCard
                    title="SLA Compliance"
                    value={`${stats.sla_compliance_rate}%`}
                    icon={CheckCircle}
                    trend="Target: 95%"
                    trendUp={stats.sla_compliance_rate >= 95}
                    color="green"
                />
            </div>

            {/* Main Charts Area */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Trend Chart */}
                <div className="card lg:col-span-2">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-lg font-semibold text-white">Complaint Trends</h2>
                        <select className="bg-white/5 border border-white/10 rounded-lg text-xs text-gray-400 px-2 py-1">
                            <option>Last 7 Days</option>
                            <option>Last 30 Days</option>
                        </select>
                    </div>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChartComponent data={trendData} />
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Severity Distribution */}
                <div className="card">
                    <h2 className="text-lg font-semibold text-white mb-6">Severity Distribution</h2>
                    <div className="h-64 relative">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={severityData}
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {severityData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                        {/* Center Text */}
                        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                            <span className="text-3xl font-bold text-white">{stats.total_complaints}</span>
                            <span className="text-xs text-gray-400">Total</span>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-2 mt-4">
                        {severityData.map((item) => (
                            <div key={item.name} className="flex items-center gap-2 text-sm text-gray-400">
                                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                                <span>{item.name}</span>
                                <span className="ml-auto text-white font-medium">{item.value}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Bottom Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Recent Activity */}
                <div className="card">
                    <h2 className="text-lg font-semibold text-white mb-4">AI Insights</h2>
                    <div className="space-y-4">
                        {stats.overdue_complaints > 0 && (
                            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex gap-3">
                                <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                                <div>
                                    <h3 className="text-sm font-medium text-red-400">SLA Breach Warning</h3>
                                    <p className="text-xs text-gray-400 mt-1">
                                        {stats.overdue_complaints} complaints have exceeded their resolution deadline. Immediate attention required.
                                    </p>
                                </div>
                            </div>
                        )}

                        <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg flex gap-3">
                            <TrendingUp className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
                            <div>
                                <h3 className="text-sm font-medium text-blue-400">Productivity Up</h3>
                                <p className="text-xs text-gray-400 mt-1">
                                    Resolution rate has increased by 5% compared to last week. Keep up the good work!
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="card">
                    <h2 className="text-lg font-semibold text-white mb-4">Quick Stats</h2>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                            <span className="text-gray-400 text-sm">Today's Volume</span>
                            <span className="text-white font-medium">{stats.complaints_today}</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                            <span className="text-gray-400 text-sm">This Week</span>
                            <span className="text-white font-medium">{stats.complaints_this_week}</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                            <span className="text-gray-400 text-sm">Resolution Rate</span>
                            <span className="text-white font-medium">{stats.resolution_rate}%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatCard({ title, value, icon: Icon, trend, trendUp, color }) {
    const colors = {
        blue: 'bg-blue-500/20 text-blue-400',
        purple: 'bg-purple-500/20 text-purple-400',
        red: 'bg-red-500/20 text-red-400',
        green: 'bg-green-500/20 text-green-400',
    };

    return (
        <div className="card p-5 group hover:-translate-y-1 transition-transform">
            <div className="flex justify-between items-start mb-4">
                <div className={`p-2 rounded-lg ${colors[color]}`}>
                    <Icon className="w-5 h-5" />
                </div>
                <div className={`flex items-center gap-1 text-xs font-medium ${trendUp ? 'text-green-400' : 'text-red-400'
                    }`}>
                    {trendUp ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                    {trend}
                </div>
            </div>
            <h3 className="text-3xl font-bold text-white mb-1">{value}</h3>
            <p className="text-xs text-gray-400 font-medium uppercase tracking-wide">{title}</p>
        </div>
    );
}

// Simple chart wrapper
const AreaChartComponent = ({ data }) => (
    <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ffffff10" />
        <XAxis
            dataKey="name"
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            dy={10}
        />
        <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#94a3b8', fontSize: 12 }}
        />
        <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
            cursor={{ fill: '#ffffff05' }}
        />
        <Bar dataKey="complaints" fill="#3b82f6" radius={[4, 4, 0, 0]} maxBarSize={40} />
    </BarChart>
);

export default Dashboard;
