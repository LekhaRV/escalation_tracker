import { Users, AlertTriangle, CheckCircle } from 'lucide-react';

export default function WorkloadWidget({ workload = [] }) {
    if (!workload || workload.length === 0) {
        return (
            <div className="card bg-surface border border-slate-200 shadow-sm rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                    <Users className="w-5 h-5 text-brand-500" />
                    <h3 className="text-lg font-bold text-logic">Team Workload</h3>
                </div>
                <p className="text-muted text-sm">No workload data available</p>
            </div>
        );
    }

    // Sort by utilization (highest first)
    const sorted = [...workload].sort((a, b) => b.utilization - a.utilization);

    return (
        <div className="card bg-surface border border-slate-200 shadow-sm rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Users className="w-5 h-5 text-brand-500" />
                    <h3 className="text-lg font-bold text-logic">Team Workload</h3>
                </div>
                <span className="text-xs text-algo font-medium bg-brand-50 px-2 py-1 rounded-full">{workload.length} members</span>
            </div>

            <div className="space-y-4">
                {sorted.slice(0, 6).map((member) => (
                    <div key={member.user_id} className="space-y-1">
                        <div className="flex items-center justify-between text-sm">
                            <span className="text-logic font-medium truncate max-w-[150px]">
                                {member.name}
                            </span>
                            <div className="flex items-center gap-2">
                                {member.utilization >= 80 ? (
                                    <AlertTriangle className="w-3 h-3 text-amber-500" />
                                ) : member.utilization < 30 ? (
                                    <CheckCircle className="w-3 h-3 text-emerald-500" />
                                ) : null}
                                <span className={`font-bold ${member.utilization >= 80 ? 'text-amber-600' :
                                    member.utilization < 30 ? 'text-emerald-600' :
                                        'text-algo'
                                    }`}>
                                    {member.utilization}%
                                </span>
                            </div>
                        </div>
                        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                            <div
                                className={`h-full rounded-full transition-all ${member.utilization >= 80 ? 'bg-amber-500' :
                                    member.utilization >= 50 ? 'bg-brand-500' :
                                        'bg-emerald-500'
                                    }`}
                                style={{ width: `${member.utilization}%` }}
                            />
                        </div>
                    </div>
                ))}
            </div>

            {workload.length > 6 && (
                <p className="text-xs text-muted mt-4 text-center font-medium">
                    +{workload.length - 6} more team members
                </p>
            )}
        </div>
    );
}
