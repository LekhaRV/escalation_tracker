import { useEffect, useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, LineChart, Line, AreaChart, Area
} from 'recharts';
import {
    AlertCircle, CheckCircle, Clock, Activity,
    TrendingUp, ArrowUpRight, ArrowDownRight, Sparkles, Brain
} from 'lucide-react';
import { analyticsService } from '../services/analyticsService';
import { useAuth } from '../context/AuthContext';
import AIAnalystWidget from '../components/dashboard/AIAnalystWidget';
import AIPatternCard from '../components/dashboard/AIPatternCard';
import AIRecommendationsPanel from '../components/dashboard/AIRecommendationsPanel';

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

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="flex items-center gap-3 text-slate-400">
                    <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                    <span>Loading dashboard...</span>
                </div>
            </div>
        );
    }

    if (!stats) return <div className="text-slate-400">Failed to load data</div>;

    const severityData = [
        { name: 'Critical', value: stats.critical_count || 0, color: '#ef4444' },
        { name: 'High', value: stats.high_count || 0, color: '#f97316' },
        { name: 'Medium', value: stats.medium_count || 0, color: '#eab308' },
        { name: 'Low', value: stats.low_count || 0, color: '#10b981' },
    ];

    const trendData = stats.daily_trends || [];

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Executive Summary Header */}
            <div className="card-highlight">
                <div className="flex items-start justify-between">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <Brain className="w-5 h-5 text-indigo-400" />
                            <span className="ai-badge">AI Dashboard</span>
                        </div>
                        <h1 className="text-2xl font-bold text-white mb-1">
                            Good {getTimeOfDay()}, {user?.name?.split(' ')[0]}
                        </h1>
                        <p className="text-slate-400 text-sm max-w-xl">
                            {getExecutiveSummary(stats)}
                        </p>
                    </div>
                    <div className="text-right hidden lg:block">
                        <div className="text-3xl font-bold text-white">{stats.sla_compliance_rate}%</div>
                        <div className="text-xs text-slate-400 uppercase tracking-wide">SLA Compliance</div>
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    title="Total Complaints"
                    value={stats.total_complaints}
                    icon={Activity}
                    subtitle={`${stats.complaints_today} today`}
                    color="indigo"
                />
                <StatCard
                    title="In Progress"
                    value={stats.in_progress_complaints}
                    icon={Clock}
                    subtitle="Active cases"
                    color="purple"
                />
                <StatCard
                    title="Critical Issues"
                    value={stats.critical_count}
                    icon={AlertCircle}
                    subtitle={stats.critical_count > 0 ? "Needs attention" : "All clear"}
                    color="red"
                    alert={stats.critical_count > 0}
                />
                <StatCard
                    title="Resolved"
                    value={stats.resolved_complaints}
                    icon={CheckCircle}
                    subtitle={`${stats.resolution_rate}% rate`}
                    color="emerald"
                />
            </div>

            {/* AI Analytics Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <AIPatternCard patterns={stats.recent_patterns} />
                <AIRecommendationsPanel insights={stats.recent_insights} />
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Trend Chart */}
                <div className="card lg:col-span-2">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-indigo-400" />
                            <h2 className="text-lg font-semibold text-white">Complaint Trends</h2>
                        </div>
                        <span className="text-xs text-slate-500">Last 7 days</span>
                    </div>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="colorComplaints" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ffffff08" />
                                <XAxis
                                    dataKey="name"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#64748b', fontSize: 12 }}
                                    dy={10}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#64748b', fontSize: 12 }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1e293b',
                                        border: '1px solid #334155',
                                        borderRadius: '12px',
                                        boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
                                    }}
                                    cursor={{ stroke: '#ffffff10' }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="complaints"
                                    stroke="#6366f1"
                                    strokeWidth={2}
                                    fillOpacity={1}
                                    fill="url(#colorComplaints)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Severity Distribution */}
                <div className="card">
                    <h2 className="text-lg font-semibold text-white mb-6">By Severity</h2>
                    <div className="h-48 relative">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={severityData}
                                    innerRadius={50}
                                    outerRadius={70}
                                    paddingAngle={4}
                                    dataKey="value"
                                >
                                    {severityData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1e293b',
                                        borderColor: '#334155',
                                        borderRadius: '8px'
                                    }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                            <span className="text-2xl font-bold text-white">{stats.total_complaints}</span>
                            <span className="text-xs text-slate-400">Total</span>
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2 mt-4">
                        {severityData.map((item) => (
                            <div key={item.name} className="flex items-center gap-2 text-sm text-slate-400">
                                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                                <span>{item.name}</span>
                                <span className="ml-auto text-white font-medium">{item.value}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <QuickStatCard
                    label="Today's Volume"
                    value={stats.complaints_today}
                    change={stats.complaints_today > 0 ? '+' + stats.complaints_today : '0'}
                />
                <QuickStatCard
                    label="This Week"
                    value={stats.complaints_this_week}
                    change="7 days"
                />
                <QuickStatCard
                    label="Overdue"
                    value={stats.overdue_complaints}
                    change={stats.overdue_complaints > 0 ? 'Action needed' : 'On track'}
                    alert={stats.overdue_complaints > 0}
                />
            </div>

            {/* AI Analyst Widget */}
            <AIAnalystWidget />
        </div>
    );
}

function getTimeOfDay() {
    const hour = new Date().getHours();
    if (hour < 12) return 'morning';
    if (hour < 17) return 'afternoon';
    return 'evening';
}

function getExecutiveSummary(stats) {
    const issues = [];
    if (stats.critical_count > 0) {
        issues.push(`${stats.critical_count} critical issue${stats.critical_count > 1 ? 's' : ''} requiring attention`);
    }
    if (stats.overdue_complaints > 0) {
        issues.push(`${stats.overdue_complaints} overdue complaint${stats.overdue_complaints > 1 ? 's' : ''}`);
    }
    if (stats.sla_compliance_rate < 90) {
        issues.push('SLA compliance below target');
    }

    if (issues.length === 0) {
        return `Your team is performing well with ${stats.resolution_rate}% resolution rate. ${stats.in_progress_complaints} cases are being actively handled.`;
    }
    return `You have ${issues.join(', ')}. ${stats.in_progress_complaints} cases are in progress.`;
}

function StatCard({ title, value, icon: Icon, subtitle, color, alert }) {
    const colors = {
        indigo: 'bg-indigo-500/15 text-indigo-400 border-indigo-500/20',
        purple: 'bg-purple-500/15 text-purple-400 border-purple-500/20',
        red: 'bg-red-500/15 text-red-400 border-red-500/20',
        emerald: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/20',
    };

    return (
        <div className={`card p-5 ${alert ? 'border-red-500/30' : ''} group hover:-translate-y-0.5 transition-all`}>
            <div className="flex justify-between items-start mb-4">
                <div className={`p-2.5 rounded-xl border ${colors[color]}`}>
                    <Icon className="w-5 h-5" />
                </div>
                {alert && (
                    <span className="flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-red-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                    </span>
                )}
            </div>
            <h3 className="text-3xl font-bold text-white mb-1">{value}</h3>
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{title}</p>
            <p className="text-xs text-slate-400 mt-1">{subtitle}</p>
        </div>
    );
}

function QuickStatCard({ label, value, change, alert }) {
    return (
        <div className={`card p-4 flex justify-between items-center ${alert ? 'border-amber-500/30' : ''}`}>
            <div>
                <span className="text-slate-400 text-sm">{label}</span>
                <div className={`text-2xl font-bold ${alert ? 'text-amber-400' : 'text-white'}`}>{value}</div>
            </div>
            <span className={`text-xs px-2 py-1 rounded-full ${alert ? 'bg-amber-500/15 text-amber-400' : 'bg-slate-700/50 text-slate-400'}`}>
                {change}
            </span>
        </div>
    );
}

export default Dashboard;
