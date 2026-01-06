import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    AlertTriangle, ArrowRight, Clock, Users,
    RefreshCw, CheckCircle, Brain, Shield,
    Activity, Inbox, Target, Zap, ExternalLink
} from 'lucide-react';
import { analyticsService } from '../services/analyticsService';
import { useAuth } from '../context/AuthContext';
import ActionablePatterns from '../components/dashboard/ActionablePatterns';

const AUTO_REFRESH_INTERVAL = 30000;

function Dashboard() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [stats, setStats] = useState(null);
    const [escalations, setEscalations] = useState([]);
    const [workload, setWorkload] = useState([]);
    const [patterns, setPatterns] = useState([]);
    const [aiInsights, setAiInsights] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [lastUpdated, setLastUpdated] = useState(new Date());

    const fetchDashboardData = useCallback(async (isRefresh = false) => {
        try {
            if (isRefresh) setRefreshing(true);
            const [dashData, escalationData, workloadData, patternsData, aiInsightsData] = await Promise.all([
                analyticsService.getAnalytics('dashboard'),
                analyticsService.getEscalations().catch(() => ({ escalations: [] })),
                analyticsService.getWorkload().catch(() => ({ workload: [] })),
                analyticsService.getPatterns().catch(() => ({ data: { patterns: [] } })),
                analyticsService.getInsights().catch(() => ({ data: { insights: [] } }))
            ]);
            setStats(dashData.data);
            setEscalations(escalationData.escalations || []);
            setWorkload(workloadData.workload || []);
            setPatterns(patternsData.data?.patterns || []);
            setAiInsights(aiInsightsData.data?.insights || []);
            setLastUpdated(new Date());
        } catch (error) {
            console.error('Failed to fetch dashboard', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, []);

    useEffect(() => { fetchDashboardData(); }, [fetchDashboardData]);
    useEffect(() => {
        const interval = setInterval(() => fetchDashboardData(true), AUTO_REFRESH_INTERVAL);
        return () => clearInterval(interval);
    }, [fetchDashboardData]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="text-center">
                    <div className="w-10 h-10 border-3 border-brand-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                    <p className="text-slate-500 font-medium">Loading...</p>
                </div>
            </div>
        );
    }

    if (!stats) return <div className="text-slate-600 p-8">Failed to load data</div>;

    return (
        <div className="space-y-5">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Command Center</h1>
                    <p className="text-slate-500 text-sm">Real-time monitoring & AI insights</p>
                </div>
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 border border-emerald-200 rounded-full">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                        </span>
                        <span className="text-emerald-700 text-xs font-semibold">LIVE</span>
                    </div>
                    <span className="text-xs text-slate-400">{formatTimeAgo(lastUpdated)}</span>
                    <button
                        onClick={() => fetchDashboardData(true)}
                        disabled={refreshing}
                        className="p-2 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-slate-600 transition-colors"
                    >
                        <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-5 gap-4">
                <StatCard label="New" value={stats.new_complaints} icon={Inbox} color="blue" onClick={() => navigate('/complaints?status=NEW')} />
                <StatCard label="In Progress" value={stats.in_progress_complaints} icon={Activity} color="violet" onClick={() => navigate('/complaints?status=IN_PROGRESS')} />
                <StatCard label="Resolved" value={stats.resolved_complaints} icon={CheckCircle} color="emerald" onClick={() => navigate('/complaints?status=RESOLVED')} />
                <StatCard label="Critical" value={stats.critical_count} icon={AlertTriangle} color="red" pulse={stats.critical_count > 0} onClick={() => navigate('/complaints?priority=CRITICAL')} />
                <StatCard label="SLA Compliance" value={`${stats.sla_compliance_rate}%`} icon={Target} color={stats.sla_compliance_rate >= 90 ? 'emerald' : 'amber'} />
            </div>

            {/* Main 3-Column Grid */}
            <div className="grid grid-cols-12 gap-5">
                {/* Escalations - 5 cols */}
                <div className="col-span-5">
                    <div className="bg-white rounded-xl border border-slate-200 shadow-soft h-full">
                        <div className="px-5 py-4 border-b border-slate-100">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-9 h-9 rounded-lg bg-red-100 flex items-center justify-center">
                                        <AlertTriangle className="w-4 h-4 text-red-600" />
                                    </div>
                                    <h2 className="font-semibold text-slate-800">Escalations</h2>
                                </div>
                                {escalations.length > 0 && (
                                    <span className="px-2.5 py-1 bg-red-50 text-red-600 text-xs font-semibold rounded-full">{escalations.length}</span>
                                )}
                            </div>
                        </div>
                        <div className="divide-y divide-slate-100 max-h-[400px] overflow-y-auto">
                            {escalations.length > 0 ? escalations.map((esc, idx) => {
                                const totalIssues = (esc.critical_high_count || 0) + (esc.overdue_count || 0);
                                const healthScore = Math.max(0, 100 - (totalIssues * 10));
                                return (
                                    <div
                                        key={idx}
                                        onClick={() => navigate(`/complaints?project_id=${esc.project_id}`)}
                                        className="flex items-center gap-4 px-5 py-3 hover:bg-slate-50 cursor-pointer group"
                                    >
                                        <div className="w-10 h-10 rounded-lg bg-brand-100 flex items-center justify-center text-brand-700 font-bold">
                                            {esc.project_name?.charAt(0) || 'P'}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="font-medium text-slate-800 group-hover:text-brand-700 truncate">{esc.project_name}</p>
                                            <div className="flex items-center gap-2 mt-1">
                                                <div className="w-20 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full ${healthScore > 80 ? 'bg-emerald-500' : healthScore > 50 ? 'bg-amber-500' : 'bg-red-500'}`}
                                                        style={{ width: `${healthScore}%` }}
                                                    />
                                                </div>
                                                <span className="text-xs text-slate-400">{healthScore}%</span>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-1.5">
                                            {esc.critical_high_count > 0 && (
                                                <span className="px-2 py-1 bg-red-50 text-red-600 text-xs font-medium rounded">{esc.critical_high_count}</span>
                                            )}
                                            {esc.overdue_count > 0 && (
                                                <span className="px-2 py-1 bg-amber-50 text-amber-600 text-xs font-medium rounded">{esc.overdue_count}</span>
                                            )}
                                        </div>
                                        <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-slate-500" />
                                    </div>
                                );
                            }) : (
                                <div className="py-12 text-center">
                                    <Shield className="w-10 h-10 mx-auto mb-2 text-emerald-200" />
                                    <p className="text-slate-500 font-medium">All Healthy</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* AI Patterns - 4 cols */}
                <div className="col-span-4">
                    <ActionablePatterns patterns={patterns} />
                </div>

                {/* AI Insights - 3 cols */}
                <div className="col-span-3">
                    <div className="bg-white rounded-xl border border-slate-200 shadow-soft h-full">
                        <div className="px-5 py-4 border-b border-slate-100">
                            <div className="flex items-center gap-3">
                                <div className="w-9 h-9 rounded-lg bg-purple-100 flex items-center justify-center">
                                    <Brain className="w-4 h-4 text-purple-600" />
                                </div>
                                <h2 className="font-semibold text-slate-800">AI Insights</h2>
                            </div>
                        </div>
                        <div className="divide-y divide-slate-100 max-h-[400px] overflow-y-auto">
                            {aiInsights.length > 0 ? aiInsights.map((insight, idx) => (
                                <div key={idx} className="px-5 py-3 hover:bg-slate-50">
                                    <div className="flex items-start gap-2">
                                        <div className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${insight.type === 'alert' ? 'bg-red-500' :
                                                insight.type === 'trend' ? 'bg-amber-500' : 'bg-purple-500'
                                            }`} />
                                        <div>
                                            <p className="text-sm font-medium text-slate-700">{insight.title}</p>
                                            <p className="text-xs text-slate-400 mt-0.5 line-clamp-2">{insight.description}</p>
                                        </div>
                                    </div>
                                </div>
                            )) : (
                                <div className="py-12 text-center">
                                    <Brain className="w-8 h-8 mx-auto mb-2 text-slate-200" />
                                    <p className="text-sm text-slate-400">No insights</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Team Workload */}
            {workload.length > 0 && (
                <div className="bg-white rounded-xl border border-slate-200 shadow-soft">
                    <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-lg bg-blue-100 flex items-center justify-center">
                                <Users className="w-4 h-4 text-blue-600" />
                            </div>
                            <h2 className="font-semibold text-slate-800">Team Workload</h2>
                        </div>
                        <button onClick={() => navigate('/users')} className="text-xs font-medium text-brand-600 hover:text-brand-700">
                            Manage Team →
                        </button>
                    </div>
                    <div className="p-5 grid grid-cols-6 gap-4">
                        {workload.slice(0, 6).map((agent, idx) => {
                            const capacity = agent.capacity || 10;
                            const current = agent.current_workload || 0;
                            const percentage = Math.round((current / capacity) * 100);
                            const isOverloaded = percentage > 80;
                            return (
                                <div key={idx} className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                                    <div className="flex items-center gap-2 mb-2">
                                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold ${isOverloaded ? 'bg-red-500' : 'bg-brand-600'}`}>
                                            {agent.name?.charAt(0)}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-slate-700 truncate">{agent.name}</p>
                                            <p className="text-xs text-slate-400">{current}/{capacity}</p>
                                        </div>
                                    </div>
                                    <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
                                        <div className={`h-full rounded-full ${isOverloaded ? 'bg-red-500' : 'bg-emerald-500'}`} style={{ width: `${Math.min(percentage, 100)}%` }} />
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}

// Professional Stat Card
function StatCard({ label, value, icon: Icon, color, pulse, onClick }) {
    const colorMap = {
        blue: { bg: 'bg-blue-100', text: 'text-blue-600', icon: 'text-blue-600' },
        violet: { bg: 'bg-violet-100', text: 'text-violet-600', icon: 'text-violet-600' },
        emerald: { bg: 'bg-emerald-100', text: 'text-emerald-600', icon: 'text-emerald-600' },
        amber: { bg: 'bg-amber-100', text: 'text-amber-600', icon: 'text-amber-600' },
        red: { bg: 'bg-red-100', text: 'text-red-600', icon: 'text-red-600' },
    };
    const c = colorMap[color] || colorMap.blue;

    return (
        <div
            onClick={onClick}
            className={`bg-white rounded-xl border border-slate-200 p-4 cursor-pointer hover:shadow-medium hover:border-slate-300 transition-all ${pulse ? 'ring-2 ring-red-100' : ''}`}
        >
            <div className="flex items-center justify-between mb-3">
                <div className={`w-10 h-10 rounded-lg ${c.bg} flex items-center justify-center`}>
                    <Icon className={`w-5 h-5 ${c.icon}`} />
                </div>
            </div>
            <p className="text-2xl font-bold text-slate-800">{value}</p>
            <p className="text-sm text-slate-500">{label}</p>
        </div>
    );
}

function formatTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    if (seconds < 60) return 'just now';
    if (seconds < 120) return '1m ago';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    return `${Math.floor(seconds / 3600)}h ago`;
}

export default Dashboard;
