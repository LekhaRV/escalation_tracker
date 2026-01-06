import { AlertTriangle, Clock, ArrowRight, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function UrgentAlertsPanel({ stats }) {
    const navigate = useNavigate();

    const hasIssues = stats.critical_count > 0 || stats.overdue_complaints > 0;

    if (!hasIssues) {
        return (
            <div className="bg-emerald-50 border border-emerald-100 rounded-lg px-4 py-2 flex items-center gap-3">
                <CheckCircle className="w-4 h-4 text-emerald-600" />
                <span className="text-emerald-700 text-sm font-medium">All Clear</span>
                <span className="text-emerald-600 text-xs">No urgent issues</span>
            </div>
        );
    }

    return (
        <div className="flex items-center gap-3 flex-wrap">
            {stats.critical_count > 0 && (
                <button
                    onClick={() => navigate('/complaints?severity=CRITICAL')}
                    className="bg-red-50 border border-red-200 rounded-lg px-3 py-2 flex items-center gap-2 hover:bg-red-100 transition-colors"
                >
                    <AlertTriangle className="w-4 h-4 text-red-600" />
                    <span className="text-red-700 text-sm font-medium">{stats.critical_count} Critical</span>
                    <ArrowRight className="w-3 h-3 text-red-500" />
                </button>
            )}
            {stats.overdue_complaints > 0 && (
                <button
                    onClick={() => navigate('/complaints?overdue=true')}
                    className="bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 flex items-center gap-2 hover:bg-amber-100 transition-colors"
                >
                    <Clock className="w-4 h-4 text-amber-600" />
                    <span className="text-amber-700 text-sm font-medium">{stats.overdue_complaints} Overdue</span>
                    <ArrowRight className="w-3 h-3 text-amber-500" />
                </button>
            )}
            {stats.in_progress_complaints > 5 && (
                <button
                    onClick={() => navigate('/complaints?status=IN_PROGRESS')}
                    className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 flex items-center gap-2 hover:bg-blue-100 transition-colors"
                >
                    <Clock className="w-4 h-4 text-blue-600" />
                    <span className="text-blue-700 text-sm font-medium">{stats.in_progress_complaints} Backlog</span>
                    <ArrowRight className="w-3 h-3 text-blue-500" />
                </button>
            )}
        </div>
    );
}
