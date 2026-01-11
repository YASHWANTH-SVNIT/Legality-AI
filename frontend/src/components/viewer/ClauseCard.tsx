import React, { useState } from 'react';
import { RiskyClause } from '../../types';
import RiskBadge from '../risk/RiskBadge';
import FeedbackButtons from '../feedback/FeedbackButtons';
import { getRiskBorderColor } from '../../utils/colors';

interface ClauseCardProps {
  clause: RiskyClause;
  index: number;
}

const ClauseCard: React.FC<ClauseCardProps> = ({ clause, index }) => {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 mb-4 border-l-4 ${getRiskBorderColor(clause.risk_level)}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-gray-900">
            Clause #{index + 1}: {clause.category}
          </h3>
          <p className="text-sm text-gray-500 mt-1">ID: {clause.chunk_id}</p>
        </div>
        <RiskBadge riskLevel={clause.risk_level} score={clause.risk_score} />
      </div>

      {/* Original Clause */}
      <div className="mb-4">
        <h4 className="font-semibold text-gray-700 mb-2">Original Clause:</h4>
        <div className="bg-red-50 border border-red-200 rounded p-4 text-sm text-gray-800">
          {clause.original_text}
        </div>
      </div>

      {/* Suggested Fix */}
      <div className="mb-4">
        <h4 className="font-semibold text-gray-700 mb-2">Suggested Fix:</h4>
        <div className="bg-green-50 border border-green-200 rounded p-4 text-sm text-gray-800">
          {clause.suggested_fix}
        </div>
        <p className="text-sm text-gray-600 mt-2 italic">{clause.fix_comment}</p>
      </div>

      {/* Key Changes */}
      <div className="mb-4">
        <h4 className="font-semibold text-gray-700 mb-2">Key Changes:</h4>
        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
          {clause.key_changes.map((change, i) => (
            <li key={i}>{change}</li>
          ))}
        </ul>
      </div>

      {/* Toggle AI Analysis */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="text-blue-600 hover:text-blue-800 text-sm font-medium mb-4 transition-colors"
      >
        {showDetails ? '▼ Hide' : '▶ Show'} AI Analysis
      </button>

      {/* AI Analysis Details */}
      {showDetails && (
        <div className="mt-4 space-y-4 pt-4 border-t">
          <div>
            <h5 className="font-semibold text-red-700 mb-2">🔴 Pessimist (Red Team):</h5>
            <p className="text-sm text-gray-700 bg-red-50 p-3 rounded">
              {clause.pessimist_analysis}
            </p>
          </div>
          <div>
            <h5 className="font-semibold text-blue-700 mb-2">🔵 Optimist (Blue Team):</h5>
            <p className="text-sm text-gray-700 bg-blue-50 p-3 rounded">
              {clause.optimist_analysis}
            </p>
          </div>
          <div>
            <h5 className="font-semibold text-purple-700 mb-2">⚖️ Arbiter (Judge):</h5>
            <p className="text-sm text-gray-700 bg-purple-50 p-3 rounded">
              {clause.arbiter_reasoning}
            </p>
          </div>
        </div>
      )}

      {/* Feedback Section */}
      <div className="mt-4 pt-4 border-t">
        <FeedbackButtons clause={clause} />
      </div>
    </div>
  );
};

export default ClauseCard;