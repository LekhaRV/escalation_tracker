import { useState, useEffect } from 'react';
import { analyticsService } from '../services/analyticsService';
import { Lightbulb, AlertTriangle, TrendingUp } from 'lucide-react';

function Analytics() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchInsights();
    }, []);

    const fetchInsights = async () => {
        try {
            const result = await analyticsService.getAnalytics('insights');
            setData(result.data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-white">AI Analytics</h1>
                <p className="text-gray-400 text-sm">Automated insights and pattern detection</p>
            </div>

            {loading ? (
                <div>Loading insights...</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {data?.insights?.map((insight, i) => (
                        <div key={i} className="card border-l-4 border-l-primary-500">
                            <div className="flex items-start gap-4">
                                <div className={`p-3 rounded-lg ${insight.type === 'trend' ? 'bg-blue-500/20 text-blue-400' :
                                        insight.type === 'alert' ? 'bg-red-500/20 text-red-400' :
                                            'bg-purple-500/20 text-purple-400'
                                    }`}>
                                    {insight.type === 'trend' && <TrendingUp className="w-6 h-6" />}
                                    {insight.type === 'alert' && <AlertTriangle className="w-6 h-6" />}
                                    {insight.type === 'recommendation' && <Lightbulb className="w-6 h-6" />}
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-white mb-2">{insight.title}</h3>
                                    <p className="text-gray-400 text-sm mb-4">{insight.description}</p>
                                    {insight.actionable && (
                                        <button className="text-xs font-bold text-primary-400 hover:text-primary-300 uppercase tracking-wide">
                                            View Recommendations →
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}

                    {(!data?.insights || data.insights.length === 0) && (
                        <div className="col-span-2 text-center p-12 card border-dashed border-white/10">
                            <Lightbulb className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                            <h3 className="text-white font-medium">No Insights Yet</h3>
                            <p className="text-gray-500 text-sm mt-1">AI generates insights weekly. Check back later.</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default Analytics;
