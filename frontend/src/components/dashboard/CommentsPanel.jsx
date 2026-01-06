import { useState } from 'react';
import { Send, MessageSquare, Clock } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { complaintService } from '../../services/complaintService';

export default function CommentsPanel({ complaintId, comments = [], onCommentAdded }) {
    const { user } = useAuth();
    const [newComment, setNewComment] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!newComment.trim()) return;

        setSubmitting(true);
        try {
            const comment = await complaintService.addComment(complaintId, newComment);
            setNewComment('');
            if (onCommentAdded) {
                onCommentAdded(comment);
            }
        } catch (error) {
            console.error('Failed to add comment', error);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="card bg-white border border-slate-200 shadow-sm p-6 rounded-xl">
            <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                <MessageSquare className="w-5 h-5" /> Internal Discussion
            </h3>

            {/* Comment List */}
            <div className="space-y-4 mb-6 max-h-[400px] overflow-y-auto custom-scrollbar">
                {comments.length > 0 ? (
                    comments.map((comment) => (
                        <div key={comment.comment_id} className="flex gap-3">
                            <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-700 shrink-0">
                                {comment.user_name?.charAt(0) || 'U'}
                            </div>
                            <div className="flex-1 bg-slate-50 rounded-lg p-3 border border-slate-100">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="font-semibold text-slate-900 text-sm">
                                        {comment.user_name}
                                    </span>
                                    <span className="text-xs text-slate-500 flex items-center gap-1">
                                        <Clock className="w-3 h-3" />
                                        {new Date(comment.created_at).toLocaleString()}
                                    </span>
                                </div>
                                <p className="text-sm text-slate-700 whitespace-pre-wrap">
                                    {comment.content}
                                </p>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="text-center py-8 text-slate-500 text-sm italic">
                        No comments yet. Start a discussion internally.
                    </div>
                )}
            </div>

            {/* Input Form */}
            {user?.role !== 'viewer' && (
                <form onSubmit={handleSubmit} className="relative">
                    <textarea
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        placeholder="Type internal note..."
                        className="input pr-12 min-h-[80px] w-full resize-none bg-white border-slate-300 text-slate-900 focus:border-primary-500 focus:ring-primary-500"
                        disabled={submitting}
                    />
                    <button
                        type="submit"
                        disabled={!newComment.trim() || submitting}
                        className="absolute right-2 bottom-2 p-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg disabled:opacity-50 disabled:bg-slate-300 transition-colors"
                    >
                        <Send className="w-4 h-4" />
                    </button>
                </form>
            )}
        </div>
    );
}
