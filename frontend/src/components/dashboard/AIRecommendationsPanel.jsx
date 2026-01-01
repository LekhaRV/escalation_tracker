import { useState } from 'react';
import { Lightbulb, TrendingUp, AlertCircle, ArrowRight, Sparkles } from 'lucide-react';

const insightIcons = {
    RECOMMENDATION: Lightbulb,
    TREND: TrendingUp,
    ALERT: AlertCircle,
};

const insightColors = {
    RECOMMENDATION: 'border-emerald-400/30 bg-emerald-500/10',
    TREND: 'border-blue-400/30 bg-blue-500/10',
    ALERT: 'border-red-400/30 bg-red-500/10',
};

const insightTextColors = {
    RECOMMENDATION: 'text-emerald-400',
    TREND: 'text-blue-400',
    ALERT: 'text-red-400',
};

const AIRecommendationsPanel = ({ insights = [] }) => {
    // const [expandedId, setExpandedId] = useState(null); // Removed expansion state
    if (!insights || insights.length === 0) {
        return (
            <div className="card-highlight">
                <div className="flex items-center gap-2 mb-4">
                    <Lightbulb className="w-5 h-5 text-emerald-400" />
                    <h3 className="text-lg font-semibold text-white">AI Insights</h3>
                    <span className="ai-badge">AI-Powered</span>
                </div>
                <div className="text-center py-8 text-slate-400">
                    <Sparkles className="w-8 h-8 mx-auto mb-3 opacity-50" />
                    <p className="text-sm">Gathering insights...</p>
                    <p className="text-xs mt-1 text-slate-500">AI insights will appear as data accumulates</p>
                </div>
            </div>
        );
    }

    // Deduplicate by title
    const uniqueInsights = [...new Map(insights.map(item => [item.title, item])).values()];

    return (
        <div className="card-highlight">
            <div className="flex items-center gap-2 mb-5">
                <Lightbulb className="w-5 h-5 text-emerald-400" />
                <h3 className="text-lg font-semibold text-white">AI Insights</h3>
                <span className="ai-badge">AI-Powered</span>
            </div>
            <div className="space-y-3">
                {uniqueInsights.slice(0, 4).map((insight) => {
                    const Icon = insightIcons[insight.type] || Lightbulb;
                    const colorClass = insightColors[insight.type] || insightColors.RECOMMENDATION;
                    const textColor = insightTextColors[insight.type] || 'text-emerald-400';
                    // const isExpanded = expandedId === insight.insight_id; 

                    return (
                        <div
                            key={insight.insight_id}
                            // onClick={() => setExpandedId(isExpanded ? null : insight.insight_id)}
                            className={`p-4 rounded-xl border ${colorClass} backdrop-blur-sm group transition-all`}
                        >
                            <div className="flex items-start gap-3">
                                <div className={`p-2 rounded-lg bg-white/5 ${textColor}`}>
                                    <Icon className="w-4 h-4" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between mb-1">
                                        <h4 className={`text-sm font-medium ${textColor}`}>
                                            {insight.title}
                                        </h4>
                                        {/* <ArrowRight className={`w-4 h-4 text-slate-500 group-hover:text-white transition-all transform ${isExpanded ? 'rotate-90' : 'group-hover:translate-x-1'}`} /> */}
                                    </div>
                                    <p className={`text-xs text-slate-400 leading-relaxed`}>
                                        {insight.description}
                                    </p>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default AIRecommendationsPanel;
