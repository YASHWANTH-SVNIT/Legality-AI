import React from 'react';
import { AnalysisResults } from '../../types';
import { getRiskColor } from '../../utils/colors';

interface RiskSummaryProps {
  results: AnalysisResults;
}

const RiskSummary: React.FC<RiskSummaryProps> = ({ results }) => {
  const { summary, document } = results;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4">Analysis Summary</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <p className="text-gray-600 mb-1">Document</p>
          <p className="font-semibold">{document.filename}</p>
        </div>
        <div>
          <p className="text-gray-600 mb-1">Total Chunks Analyzed</p>
          <p className="font-semibold">{document.total_chunks}</p>
        </div>
      </div>

      <div className="border-t pt-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold">Overall Risk</h3>
          <span className={`px-4 py-2 rounded-lg text-lg font-bold ${getRiskColor(summary.overall_risk)}`}>
            {summary.overall_risk}
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="p-4 bg-red-50 rounded-lg">
            <p className="text-3xl font-bold text-red-600">{document.risky_clauses_found}</p>
            <p className="text-sm text-gray-600 mt-1">Risky Clauses</p>
          </div>
          <div className="p-4 bg-orange-50 rounded-lg">
            <p className="text-3xl font-bold text-orange-600">{summary.compound_risks_found}</p>
            <p className="text-sm text-gray-600 mt-1">Compound Risks</p>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-3xl font-bold text-blue-600">{summary.average_risk_score.toFixed(1)}</p>
            <p className="text-sm text-gray-600 mt-1">Avg Risk Score</p>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg">
            <p className="text-3xl font-bold text-purple-600">{summary.categories_flagged.length}</p>
            <p className="text-sm text-gray-600 mt-1">Categories</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskSummary;