import { Clock } from 'lucide-react';

/**
 * Calculate SLA remaining display from deadline date
 */
export function getSlaStatus(slaDeadline, status) {
    if (!slaDeadline) return null;

    if (['resolved', 'closed'].includes(status?.toLowerCase())) {
        return null; // Don't show countdown for resolved issues
    }

    const deadline = new Date(slaDeadline);
    const now = new Date();
    const diffMs = deadline - now;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

    if (diffMs < 0) {
        const overdueDays = Math.abs(diffDays);
        return {
            text: `${overdueDays}d overdue`,
            color: 'red',
            urgent: true
        };
    }

    if (diffDays <= 3) {
        return {
            text: diffDays === 0 ? `${diffHours}h left` : `${diffDays}d left`,
            color: 'red',
            urgent: true
        };
    }

    if (diffDays <= 14) {
        return {
            text: `${diffDays}d left`,
            color: 'amber',
            urgent: false
        };
    }

    return {
        text: `${diffDays}d left`,
        color: 'emerald',
        urgent: false
    };
}

export default function SlaCountdown({ deadline, status, showIcon = true, size = 'sm' }) {
    const slaStatus = getSlaStatus(deadline, status);

    if (!slaStatus) {
        // Option: return <span className="text-emerald-600 text-xs font-medium">Resolved</span>;
        // But user asked why days remaining is showing, implies they might expect nothing or a static "Resolved" text?
        // Let's return nothing or a subtle dash if active.
        // If status is resolved, we might want to say "Met" or nothing.
        // Given the user query, simply hiding the countdown is the safest first step.
        return status && ['resolved', 'closed'].includes(status.toLowerCase())
            ? <span className="text-emerald-600 text-xs font-medium border border-emerald-200 bg-emerald-50 px-2 py-0.5 rounded-full">Resolved</span>
            : <span className="text-slate-400 text-xs">--</span>;
    }

    const sizeClasses = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-3 py-1';
    const colorClasses = {
        red: 'bg-red-50 text-red-600 border-red-100',
        amber: 'bg-amber-50 text-amber-600 border-amber-100',
        emerald: 'bg-emerald-50 text-emerald-600 border-emerald-100'
    };

    return (
        <span className={`inline-flex items-center gap-1 rounded-full border ${sizeClasses} ${colorClasses[slaStatus.color]} ${slaStatus.urgent ? 'animate-pulse' : ''}`}>
            {showIcon && <Clock className="w-3 h-3" />}
            {slaStatus.text}
        </span>
    );
}
