import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAnalysis } from '../hooks/useAnalysis';
import RiskSummary from '../components/risk/RiskSummary';
import ClauseCard from '../components/viewer/ClauseCard';

const AnalysisPage: React.FC = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();
  const { status, results, error } = useAnalysis(analysisId!);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-xl mb-4">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mb-4"></div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Analyzing Contract...</h2>
          <p className="text-gray-600">{status?.filename}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Contract Analysis</h1>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg"
          >
            ← New Analysis
          </button>
        </div>

        <RiskSummary results={results} />

        {results.compound_risks.length > 0 && (
          <div className="bg-orange-50 border-l-4 border-orange-500 p-6 mb-6 rounded-lg">
            <h3 className="text-xl font-bold text-orange-900 mb-4">
              ⚠️ Compound Risks Detected
            </h3>
            {results.compound_risks.map((risk, i) => (
              <div key={i} className="mb-4 last:mb-0">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-bold">{risk.risk_type}</span>
                  <span className="px-2 py-1 bg-orange-200 text-orange-900 rounded text-sm">
                    {risk.severity}
                  </span>
                </div>
                <p className="text-sm text-gray-700 mb-2">{risk.description}</p>
                <p className="text-sm text-gray-600 italic">💡 {risk.mitigation}</p>
              </div>
            ))}
          </div>
        )}

        <div>
          <h2 className="text-2xl font-bold mb-4">Risky Clauses</h2>
          {results.risky_clauses.map((clause, i) => (
            <ClauseCard key={clause.chunk_id} clause={clause} index={i} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default AnalysisPage;