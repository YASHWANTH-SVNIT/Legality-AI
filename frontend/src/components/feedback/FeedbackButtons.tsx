import React, { useState } from 'react';
import { submitFeedback } from '../../services/api';
import { RiskyClause } from '../../types';

interface FeedbackButtonsProps {
  clause: RiskyClause;
  analysisId?: string;
}

const FeedbackButtons: React.FC<FeedbackButtonsProps> = ({ clause, analysisId }) => {
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const [comment, setComment] = useState('');

  const handleFeedback = async (
    type: 'false-positive' | 'false-negative' | 'approve-fix',
    approved?: boolean
  ) => {
    setLoading(true);
    try {
      await submitFeedback(type, {
        chunk_id: clause.chunk_id,
        clause_text: clause.original_text,
        category: clause.category,
        system_risk_score: clause.risk_score,
        suggested_fix: clause.suggested_fix,
        approved: approved,
        user_comment: comment,
        user_id: 'anonymous',
        analysis_id: analysisId,
        pessimist_analysis: clause.pessimist_analysis,
        optimist_analysis: clause.optimist_analysis,
        arbiter_reasoning: clause.arbiter_reasoning
      });
      setSubmitted(true);
    } catch (err) {
      console.error('Feedback failed:', err);
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="text-sm text-green-600 font-medium p-3 bg-green-50 rounded-lg border border-green-200">
        ✓ Thank you! Your feedback helps us improve.
      </div>
    );
  }

  return (
    <div className="space-y-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
      <div className="space-y-2">
        <label htmlFor="feedback-comment" className="block text-xs font-semibold text-gray-700 uppercase tracking-wider">
          Optional Comment
        </label>
        <textarea
          id="feedback-comment"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Tell us why this is safe or if the fix could be better..."
          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 resize-none"
          rows={2}
        />
      </div>

      <div className="space-y-2">
        <p className="text-xs text-gray-600 font-medium">Was this analysis helpful?</p>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => handleFeedback('false-positive')}
            disabled={loading}
            className="px-4 py-2 text-xs font-bold bg-white hover:bg-gray-100 text-gray-700 rounded-lg border border-gray-300 shadow-sm disabled:opacity-50 transition-all active:scale-95"
          >
            Not Risky
          </button>
          <button
            onClick={() => handleFeedback('approve-fix', true)}
            disabled={loading}
            className="px-4 py-2 text-xs font-bold bg-green-600 hover:bg-green-700 text-white rounded-lg shadow-sm disabled:opacity-50 transition-all active:scale-95"
          >
            👍 Good Fix
          </button>
          <button
            onClick={() => handleFeedback('approve-fix', false)}
            disabled={loading}
            className="px-4 py-2 text-xs font-bold bg-red-50 hover:bg-red-100 text-red-700 rounded-lg border border-red-300 shadow-sm disabled:opacity-50 transition-all active:scale-95"
          >
            👎 Bad Fix
          </button>
        </div>
      </div>
    </div>
  );
};

export default FeedbackButtons;