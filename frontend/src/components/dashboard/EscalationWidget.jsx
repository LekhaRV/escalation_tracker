import { AlertTriangle, ExternalLink, Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

function EscalationWidget({ escalations = [], isRefreshing }) {
    const navigate = useNavigate();

    if (!escalations.length) {
        return (
            <div className="card bg-white border border-slate-200 shadow-sm rounded-xl p-6">
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" />
                    Projects in Escalation
                </h3>
                <div className="text-center py-8 text-slate-500">
                    <AlertTriangle className="w-8 h-8 mx-auto mb-2 opacity-50 text-slate-400" />
                    <p className="text-sm font-medium">No projects in escalation</p>
                    <p className="text-xs mt-1">All projects are within SLA</p>
                </div>
            </div>
        );
    }

    return (
        <div className="card bg-white border border-slate-200 shadow-sm rounded-xl p-6">
            <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-red-500" />
                Projects in Escalation
                <span className="ml-auto bg-red-50 text-red-600 border border-red-100 px-2 py-0.5 rounded-full text-xs font-bold">
                    {escalations.length}
                </span>
            </h3>

            <div className="space-y-3">
                {escalations.slice(0, 5).map((project) => (
                    <div
                        key={project.project_id}
                        className="bg-slate-50 rounded-lg p-3 border border-slate-200 hover:border-red-300 hover:bg-white hover:shadow-sm transition-all cursor-pointer group"
                        onClick={() => navigate(`/complaints?project_id=${project.project_id}`)}
                    >
                        <div className="flex items-start justify-between mb-2">
                            <div className="flex-1">
                                <h4 className="font-bold text-slate-900 group-hover:text-red-600 transition-colors flex items-center gap-2">
                                    {project.project_name}
                                    <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                                </h4>
                                <p className="text-xs text-slate-500 font-medium">{project.client_name}</p>
                            </div>
                        </div>

                        <div className="flex gap-3 text-xs font-medium">
                            {project.critical_high_count > 0 && (
                                <div className="flex items-center gap-1 text-red-600">
                                    <AlertTriangle className="w-3 h-3" />
                                    <span>{project.critical_high_count} Critical/High</span>
                                </div>
                            )}
                            {project.overdue_count > 0 && (
                                <div className="flex items-center gap-1 text-amber-600">
                                    <Clock className="w-3 h-3" />
                                    <span>{project.overdue_count} Overdue</span>
                                </div>
                            )}
                        </div>

                        <div className="mt-2 pt-2 border-t border-slate-200">
                            <div className="flex items-center justify-between text-xs">
                                <span className="text-slate-500 font-medium">Total Open</span>
                                <span className="text-slate-900 font-bold">{project.total_open}</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {escalations.length > 5 && (
                <button
                    onClick={() => navigate('/complaints')}
                    className="w-full mt-4 py-2 text-center text-xs font-semibold text-primary-600 hover:text-primary-700 transition-colors bg-primary-50 rounded-lg"
                >
                    View all {escalations.length} escalated projects →
                </button>
            )}
        </div>
    );
}

export default EscalationWidget;
