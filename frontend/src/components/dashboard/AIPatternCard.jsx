import { TrendingUp, RefreshCw, AlertTriangle, Sparkles } from 'lucide-react';

const patternIcons = {
    RECURRING: RefreshCw,
    TRENDING: TrendingUp,
    SYSTEMIC: AlertTriangle,
};

const patternColors = {
    RECURRING: 'from-purple-500/20 to-indigo-500/20 border-purple-400/30 text-purple-300',
    TRENDING: 'from-amber-500/20 to-orange-500/20 border-amber-400/30 text-amber-300',
    SYSTEMIC: 'from-red-500/20 to-rose-500/20 border-red-400/30 text-red-300',
};

const AIPatternCard = ({ patterns = [] }) => {
    if (!patterns || patterns.length === 0) {
        return (
            <div className="card-highlight">
                <div className="flex items-center gap-2 mb-4">
                    <Sparkles className="w-5 h-5 text-indigo-400" />
                    <h3 className="text-lg font-semibold text-white">AI Detected Patterns</h3>
                    <span className="ai-badge">AI-Powered</span>
                </div>
                <div className="text-center py-8 text-slate-400">
                    <RefreshCw className="w-8 h-8 mx-auto mb-3 opacity-50" />
                    <p className="text-sm">No patterns detected yet.</p>
                    <p className="text-xs mt-1 text-slate-500">AI is analyzing your complaint data...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="card-highlight">
            <div className="flex items-center gap-2 mb-5">
                <Sparkles className="w-5 h-5 text-indigo-400" />
                <h3 className="text-lg font-semibold text-white">AI Detected Patterns</h3>
                <span className="ai-badge">AI-Powered</span>
            </div>
            <div className="space-y-3">
                {patterns.slice(0, 4).map((pattern) => {
                    const Icon = patternIcons[pattern.type] || TrendingUp;
                    const colorClass = patternColors[pattern.type] || patternColors.TRENDING;
                    const confidence = Math.round((pattern.confidence || 0) * 100);

                    return (
                        <div
                            key={pattern.pattern_id}
                            className={`p-4 rounded-xl bg-gradient-to-r ${colorClass} border backdrop-blur-sm transition-all hover:scale-[1.01]`}
                        >
                            <div className="flex items-start gap-3">
                                <div className="p-2 rounded-lg bg-white/10">
                                    <Icon className="w-4 h-4" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="text-xs font-medium uppercase tracking-wide opacity-80">
                                            {pattern.type}
                                        </span>
                                        {confidence > 0 && (
                                            <span className="text-xs bg-white/10 px-2 py-0.5 rounded-full">
                                                {confidence}% confidence
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-sm text-white/90 leading-relaxed">
                                        {pattern.description}
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

export default AIPatternCard;
