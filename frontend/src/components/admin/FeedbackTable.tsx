import React, { useEffect, useState } from 'react';
import { adminApi } from '../../services/api';

const FeedbackTable = () => {
    const [feedback, setFeedback] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedFeedback, setSelectedFeedback] = useState<any | null>(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const data = await adminApi.getFeedback({ limit: 100 });
            setFeedback(data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateStatus = async (id: number, status: string) => {
        try {
            await adminApi.updateFeedbackStatus(id, status);
            setFeedback(prev => prev.map(f => f.id === id ? { ...f, status } : f));
        } catch (e: any) {
            console.error('Failed to update status:', e);
            alert(`Failed to update status. Please ensure the backend is running.`);
        }
    };

    const handleBatchSync = async () => {
        const key = prompt("Please enter Admin Key to confirm batch sync to Vector DB:");
        if (!key) return;

        try {
            const res = await adminApi.batchSync(key);
            alert(`Batch sync completed successfully! Synced ${res.count} items.`);
            loadData();
        } catch (e: any) {
            alert(`Sync failed: ${e.response?.data?.detail || "Invalid Key"}`);
        }
    };

    const pendingReview = feedback.filter(f =>
        (f.status === 'pending' || !f.status) && f.feedback_type === 'false-positive'
    );

    const approvedSuggestions = feedback.filter(f =>
        f.status === 'approved' && f.feedback_type === 'false-positive'
    );

    if (loading) return (
        <div className="flex flex-col items-center justify-center p-20 space-y-4">
            <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
            <p className="text-gray-500 font-bold animate-pulse uppercase tracking-widest text-xs">Loading Legal Feedback...</p>
        </div>
    );

    const FeedbackCard = ({ f, isApproved = false }: { f: any, isApproved?: boolean }) => {
        return (
            <div className={`bg-white rounded-2xl border ${isApproved ? 'border-green-100' : 'border-gray-100'} shadow-sm overflow-hidden transition-all duration-300 hover:shadow-md`}>
                <div className="p-6">
                    <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center gap-3">
                            <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                                {new Date(f.timestamp).toLocaleDateString()}
                            </span>
                            <span className={`px-3 py-1 rounded-lg text-xs font-black uppercase tracking-tight ${isApproved ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-800'}`}>
                                {f.category}
                            </span>
                        </div>
                        <div className="flex gap-2">
                            {!isApproved ? (
                                <>
                                    <button
                                        onClick={() => handleUpdateStatus(f.id, 'approved')}
                                        className="px-4 py-2 bg-emerald-500 text-white text-[11px] font-black rounded-xl shadow-md shadow-emerald-200 hover:bg-emerald-600 transition-all active:scale-95"
                                    >
                                        APPROVE
                                    </button>
                                    <button
                                        onClick={() => handleUpdateStatus(f.id, 'rejected')}
                                        className="px-4 py-2 bg-white text-rose-500 text-[11px] font-black rounded-xl border border-rose-100 hover:bg-rose-50 transition-all active:scale-95"
                                    >
                                        REJECT
                                    </button>
                                </>
                            ) : (
                                <button
                                    onClick={() => handleUpdateStatus(f.id, 'pending')}
                                    className="px-4 py-2 bg-white text-gray-500 text-[11px] font-black rounded-xl border border-gray-100 hover:bg-gray-50 transition-all active:scale-95"
                                >
                                    REMOVE FROM SYNC
                                </button>
                            )}
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="relative">
                            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Clause Content</h4>
                            <div className="bg-gray-50 p-4 rounded-xl border border-gray-100 max-h-24 overflow-hidden">
                                <p className="text-gray-700 leading-relaxed font-medium">
                                    {f.clause_text}
                                </p>
                            </div>
                            {f.clause_text.length > 150 && (
                                <div className="absolute inset-x-0 bottom-0 h-10 bg-gradient-to-t from-gray-50 to-transparent pointer-events-none"></div>
                            )}
                        </div>

                        <div className="flex justify-between items-end pt-2">
                            <div className="flex-1 mr-4">
                                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">User Comment</h4>
                                <div className="bg-indigo-50/30 p-3 rounded-xl border border-indigo-100/50">
                                    <p className="text-sm text-indigo-900 leading-relaxed italic">
                                        {f.user_comment || "No comment provided by user."}
                                    </p>
                                </div>
                            </div>
                            <button
                                onClick={() => setSelectedFeedback(f)}
                                className="text-indigo-600 font-bold text-[11px] uppercase tracking-widest hover:text-indigo-800 transition-colors py-2 px-4 bg-indigo-50 rounded-lg"
                            >
                                View Full Card
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="flex flex-col mt-4 space-y-12 pb-32 max-w-6xl mx-auto">
            {/* Header Section */}
            <div className="bg-white p-8 rounded-[2.5rem] shadow-sm border border-gray-50">
                <h2 className="text-3xl font-black text-gray-900 tracking-tighter">Legal Feedback Review</h2>
                <p className="text-gray-500 mt-2 font-medium">Finalize user suggestions and update the RAG Knowledge Base.</p>
            </div>

            {/* Section 1: Pending Reviews */}
            <div className="space-y-6">
                <div className="flex items-center gap-3 px-2">
                    <div className="h-6 w-1.5 bg-amber-500 rounded-full"></div>
                    <h3 className="text-xl font-black text-gray-900 uppercase tracking-tight">Pending Reviews ({pendingReview.length})</h3>
                </div>

                {pendingReview.length === 0 ? (
                    <div className="bg-white rounded-[2rem] border border-dashed border-gray-200 p-20 text-center">
                        <span className="text-4xl mb-4 block">⚖️</span>
                        <p className="text-gray-400 font-bold uppercase tracking-widest text-xs">All clear! No pending reviews.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 gap-6">
                        {pendingReview.map((f) => (
                            <FeedbackCard key={f.id} f={f} />
                        ))}
                    </div>
                )}
            </div>

            {/* Section 2: Approved Suggestions */}
            <div className="space-y-6">
                <div className="flex justify-between items-center px-2">
                    <div className="flex items-center gap-3">
                        <div className="h-6 w-1.5 bg-emerald-500 rounded-full"></div>
                        <h3 className="text-xl font-black text-gray-900 uppercase tracking-tight">Approved Suggestions ({approvedSuggestions.length})</h3>
                    </div>
                    {approvedSuggestions.length > 0 && (
                        <button
                            onClick={handleBatchSync}
                            className="inline-flex items-center px-8 py-4 bg-indigo-600 text-white text-xs font-black rounded-[1.5rem] shadow-xl shadow-indigo-100 hover:bg-indigo-700 transition-all active:scale-95 uppercase tracking-widest"
                        >
                            ⚡ UPDATE KNOWLEDGE BASE
                        </button>
                    )}
                </div>

                {approvedSuggestions.length === 0 ? (
                    <div className="bg-gray-50/50 rounded-[2rem] border border-gray-100 p-16 text-center">
                        <p className="text-gray-400 font-bold uppercase tracking-widest text-xs">No clauses ready for vector sync yet.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 gap-4">
                        {approvedSuggestions.map((f) => (
                            <FeedbackCard key={f.id} f={f} isApproved={true} />
                        ))}
                    </div>
                )}
            </div>

            {/* Modal for Full Details */}
            {selectedFeedback && (
                <div className="fixed inset-0 bg-gray-900/80 backdrop-blur-md flex items-center justify-center p-4 z-50 animate-in fade-in zoom-in duration-200">
                    <div className="bg-white rounded-[2.5rem] max-w-5xl w-full p-10 shadow-2xl relative overflow-hidden border border-white/20">
                        <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"></div>

                        <div className="flex justify-between items-start mb-8">
                            <div>
                                <h3 className="text-2xl font-black text-gray-900 tracking-tight">Analysis Deep-Dive</h3>
                                <div className="flex items-center gap-3 mt-2">
                                    <span className="text-xs font-bold text-gray-400">{new Date(selectedFeedback.timestamp).toLocaleDateString()}</span>
                                    <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-lg text-[10px] font-black uppercase tracking-widest">{selectedFeedback.category}</span>
                                    {selectedFeedback.system_risk_score && (
                                        <span className="px-3 py-1 bg-rose-50 text-rose-600 rounded-lg text-[10px] font-black uppercase tracking-widest border border-rose-100">
                                            Risk: {selectedFeedback.system_risk_score}/100
                                        </span>
                                    )}
                                </div>
                            </div>
                            <button
                                onClick={() => setSelectedFeedback(null)}
                                className="w-10 h-10 flex items-center justify-center bg-gray-100 hover:bg-gray-200 rounded-full transition-colors text-xl font-bold"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-h-[65vh] overflow-y-auto pr-4 custom-scrollbar">
                            {/* Left Column: Clause & Fix */}
                            <div className="space-y-6">
                                <div>
                                    <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">Original Clause</h4>
                                    <div className="bg-gray-50 p-6 rounded-3xl border border-gray-100">
                                        <p className="text-gray-700 leading-relaxed font-medium text-sm text-justify">
                                            "{selectedFeedback.clause_text}"
                                        </p>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="text-[10px] font-black text-emerald-600 uppercase tracking-widest mb-3">Suggested Legal Fix</h4>
                                    <div className="bg-emerald-50/30 p-6 rounded-3xl border border-emerald-100/50">
                                        <p className="text-emerald-900 leading-relaxed font-bold text-sm">
                                            {selectedFeedback.suggested_fix || "No legal fix was generated for this clause."}
                                        </p>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="text-[10px] font-black text-indigo-500 uppercase tracking-widest mb-3">User Rationale</h4>
                                    <div className="bg-indigo-50/50 p-6 rounded-3xl border border-indigo-100/50">
                                        <p className="text-indigo-900 leading-relaxed font-bold italic text-sm">
                                            {selectedFeedback.user_comment || "No specific comment provided."}
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Right Column: Debate & Logic */}
                            <div className="space-y-6">
                                <div>
                                    <h4 className="text-[10px] font-black text-rose-500 uppercase tracking-widest mb-3">Pessimist Argument (Risk)</h4>
                                    <div className="bg-rose-50/30 p-6 rounded-3xl border border-rose-100/50">
                                        <p className="text-rose-900 leading-relaxed text-sm">
                                            {selectedFeedback.pessimist_analysis || "Debate data not captured for this record."}
                                        </p>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="text-[10px] font-black text-emerald-500 uppercase tracking-widest mb-3">Optimist Defense (Context)</h4>
                                    <div className="bg-emerald-50/30 p-6 rounded-3xl border border-emerald-100/50">
                                        <p className="text-emerald-900 leading-relaxed text-sm">
                                            {selectedFeedback.optimist_analysis || "Debate data not captured for this record."}
                                        </p>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="text-[10px] font-black text-amber-600 uppercase tracking-widest mb-3">Arbiter Final Reasoning</h4>
                                    <div className="bg-amber-50/30 p-6 rounded-3xl border border-amber-100/50">
                                        <p className="text-amber-900 leading-relaxed font-medium text-sm italic">
                                            {selectedFeedback.arbiter_reasoning || "Debate data not captured for this record."}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="mt-10 flex justify-end">
                            <button
                                onClick={() => setSelectedFeedback(null)}
                                className="px-10 py-4 bg-gray-900 text-white font-black rounded-[1.25rem] hover:bg-gray-800 transition-all active:scale-95 shadow-xl shadow-gray-200 uppercase tracking-widest text-xs"
                            >
                                Back to Review
                            </button>
                        </div>
                    </div>
                </div>
            )}
            <style>{`
                .custom-scrollbar::-webkit-scrollbar {
                    width: 6px;
                }
                .custom-scrollbar::-webkit-scrollbar-track {
                    background: transparent;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: #E5E7EB;
                    border-radius: 10px;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                    background: #D1D5DB;
                }
            `}</style>
        </div>
    );
};

export default FeedbackTable;
