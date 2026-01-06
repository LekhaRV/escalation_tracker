import { useState } from 'react';
import { ArrowRight, X, Zap, TrendingUp, AlertOctagon, Repeat, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const PATTERN_CONFIG = {
    SYSTEMIC: {
        icon: AlertOctagon,
        bg: 'bg-red-100',
        iconColor: 'text-red-600',
        cardBg: 'bg-red-50',
        border: 'border-red-200',
        badge: 'bg-red-100 text-red-700',
        btn: 'bg-red-600 hover:bg-red-700'
    },
    TRENDING: {
        icon: TrendingUp,
        bg: 'bg-violet-100',
        iconColor: 'text-violet-600',
        cardBg: 'bg-violet-50',
        border: 'border-violet-200',
        badge: 'bg-violet-100 text-violet-700',
        btn: 'bg-violet-600 hover:bg-violet-700'
    },
    RECURRING: {
        icon: Repeat,
        bg: 'bg-amber-100',
        iconColor: 'text-amber-600',
        cardBg: 'bg-amber-50',
        border: 'border-amber-200',
        badge: 'bg-amber-100 text-amber-700',
        btn: 'bg-amber-600 hover:bg-amber-700'
    }
};

const ActionablePatterns = ({ patterns = [] }) => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [actioned, setActioned] = useState([]);
    const [dismissed, setDismissed] = useState([]);

    const handleAction = (pattern) => {
        setActioned([...actioned, pattern.pattern_id]);
        if (pattern.affected_complaints && pattern.affected_complaints.length > 0) {
            navigate(`/complaints?ids=${pattern.affected_complaints.join(',')}`);
        } else {
            navigate(`/complaints?category=${pattern.type}`);
        }
    };

    const activePatterns = patterns.filter(p => !actioned.includes(p.pattern_id) && !dismissed.includes(p.pattern_id));

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-soft h-full flex flex-col">
            {/* Header */}
            <div className="px-5 py-4 border-b border-slate-100">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg bg-violet-100 flex items-center justify-center">
                            <Zap className="w-4 h-4 text-violet-600" />
                        </div>
                        <h2 className="font-semibold text-slate-800">AI Patterns</h2>
                    </div>
                    {activePatterns.length > 0 && (
                        <span className="px-2.5 py-1 bg-violet-50 text-violet-600 text-xs font-semibold rounded-full">
                            {activePatterns.length}
                        </span>
                    )}
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 max-h-[400px]">
                {activePatterns.length > 0 ? activePatterns.map((pattern) => {
                    const config = PATTERN_CONFIG[pattern.type] || PATTERN_CONFIG.RECURRING;
                    const Icon = config.icon;
                    const confidence = Math.round((pattern.confidence || 0.8) * 100);

                    return (
                        <div
                            key={pattern.pattern_id}
                            className={`p-4 rounded-lg border ${config.border} ${config.cardBg}`}
                        >
                            {/* Header */}
                            <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center gap-2">
                                    <div className={`w-7 h-7 rounded-md ${config.bg} flex items-center justify-center`}>
                                        <Icon className={`w-3.5 h-3.5 ${config.iconColor}`} />
                                    </div>
                                    <span className={`text-[10px] font-bold uppercase ${config.iconColor}`}>
                                        {pattern.type}
                                    </span>
                                    <span className={`text-[10px] px-2 py-0.5 rounded-full ${config.badge}`}>
                                        {confidence}%
                                    </span>
                                </div>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setDismissed([...dismissed, pattern.pattern_id]);
                                    }}
                                    className="text-slate-300 hover:text-slate-500 p-0.5"
                                >
                                    <X className="w-3.5 h-3.5" />
                                </button>
                            </div>

                            {/* Description */}
                            <p className="text-sm text-slate-700 mb-3 line-clamp-2">{pattern.description}</p>

                            {/* Confidence Bar */}
                            <div className="mb-3">
                                <div className="h-1.5 bg-white rounded-full overflow-hidden">
                                    <div className={`h-full rounded-full ${config.btn.split(' ')[0]}`} style={{ width: `${confidence}%` }} />
                                </div>
                            </div>

                            {/* Action */}
                            <button
                                onClick={() => handleAction(pattern)}
                                className={`w-full py-2 rounded-lg text-xs font-semibold text-white flex items-center justify-center gap-2 transition-colors ${config.btn}`}
                            >
                                View Related <ArrowRight className="w-3 h-3" />
                            </button>
                        </div>
                    );
                }) : (
                    <div className="py-12 text-center">
                        <CheckCircle className="w-10 h-10 mx-auto mb-2 text-slate-200" />
                        <p className="text-sm text-slate-500 font-medium">No patterns</p>
                        <p className="text-xs text-slate-400">Systems normal</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ActionablePatterns;
