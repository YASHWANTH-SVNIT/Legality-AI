import React, { useState } from 'react';
import { submitFeedback } from '../../services/api';
import { RiskyClause } from '../../types';

interface FeedbackButtonsProps {
  clause: RiskyClause;
}

const FeedbackButtons: React.FC<FeedbackButtonsProps> = ({ clause }) => {
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

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
        user_id: 'anonymous'
      });
      setSubmitted(true);
      setTimeout(() => setSubmitted(false), 3000);
    } catch (err) {
      console.error('Feedback failed:', err);
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="text-sm text-green-600 font-medium">
        ✓ Thank you for your feedback!
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <p className="text-xs text-gray-600 font-medium">Was this analysis helpful?</p>
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => handleFeedback('false-positive')}
          disabled={loading}
          className="px-3 py-1.5 text-xs font-medium bg-gray-100 hover:bg-gray-200 text-gray-700 rounded border border-gray-300 disabled:opacity-50 transition-colors"
        >
          Not Risky
        </button>
        <button
          onClick={() => handleFeedback('approve-fix', true)}
          disabled={loading}
          className="px-3 py-1.5 text-xs font-medium bg-green-50 hover:bg-green-100 text-green-700 rounded border border-green-300 disabled:opacity-50 transition-colors"
        >
          👍 Good Fix
        </button>
        <button
          onClick={() => handleFeedback('approve-fix', false)}
          disabled={loading}
          className="px-3 py-1.5 text-xs font-medium bg-red-50 hover:bg-red-100 text-red-700 rounded border border-red-300 disabled:opacity-50 transition-colors"
        >
          👎 Bad Fix
        </button>
      </div>
    </div>
  );
};

export default FeedbackButtons;