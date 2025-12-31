import { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Bot, User, Loader2 } from 'lucide-react';
import { analyticsService } from '../../services/analyticsService';

const AIAnalystWidget = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: 'Hello! I am your AI Data Analyst. Ask me anything about your complaint data, trends, or insights.'
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isOpen]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!inputValue.trim() || isLoading) return;

        const userMessage = inputValue;
        setInputValue('');
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setIsLoading(true);

        try {
            const response = await analyticsService.askAnalyst(userMessage);
            setMessages(prev => [...prev, { role: 'assistant', content: response.answer }]);
        } catch (error) {
            console.error("AI Analyst Error:", error);
            setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error while analyzing your data." }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
            {/* Chat Window */}
            {isOpen && (
                <div className="mb-4 w-80 md:w-96 bg-slate-800 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden flex flex-col animate-in slide-in-from-bottom-10 fade-in duration-200">
                    {/* Header */}
                    <div className="bg-slate-900/50 p-4 border-b border-slate-700 flex justify-between items-center backdrop-blur-sm">
                        <div className="flex items-center gap-2 text-white font-medium">
                            <Bot className="w-5 h-5 text-blue-400" />
                            <span>AI Analyst</span>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="text-gray-400 hover:text-white transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Messages Area */}
                    <div className="h-96 overflow-y-auto p-4 space-y-4 bg-slate-900/20">
                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                            >
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'assistant' ? 'bg-blue-500/10 text-blue-400' : 'bg-purple-500/10 text-purple-400'
                                    }`}>
                                    {msg.role === 'assistant' ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
                                </div>
                                <div className={`rounded-2xl p-3 text-sm max-w-[80%] ${msg.role === 'assistant'
                                        ? 'bg-slate-700/50 text-gray-200 rounded-tl-none'
                                        : 'bg-blue-600 text-white rounded-tr-none'
                                    }`}>
                                    {msg.content}
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex gap-3">
                                <div className="w-8 h-8 rounded-full bg-blue-500/10 text-blue-400 flex items-center justify-center shrink-0">
                                    <Bot className="w-5 h-5" />
                                </div>
                                <div className="bg-slate-700/50 rounded-2xl p-3 rounded-tl-none">
                                    <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <form onSubmit={handleSubmit} className="p-4 bg-slate-900/50 border-t border-slate-700">
                        <div className="relative">
                            <input
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                placeholder="Ask about complaints..."
                                className="w-full bg-slate-800 text-white text-sm rounded-full pl-4 pr-12 py-3 border border-slate-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 placeholder-gray-500"
                            />
                            <button
                                type="submit"
                                disabled={!inputValue.trim() || isLoading}
                                className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors"
                            >
                                <Send className="w-4 h-4" />
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Toggle Button */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="group flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-all hover:scale-105 active:scale-95"
                >
                    <MessageSquare className="w-6 h-6" />
                    <span className="max-w-0 overflow-hidden group-hover:max-w-xs transition-all duration-300 ease-in-out whitespace-nowrap">
                        Ask AI Analyst
                    </span>
                </button>
            )}
        </div>
    );
};

export default AIAnalystWidget;
