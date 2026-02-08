import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAnalysis } from '../hooks/useAnalysis';
import RiskSummary from '../components/risk/RiskSummary';
import ClauseCard from '../components/viewer/ClauseCard';
import Footer from '../components/common/Footer';

const AnalysisPage: React.FC = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();
  const { status, results, error } = useAnalysis(analysisId!);
  const [showDisclaimer, setShowDisclaimer] = useState(true);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-10 rounded-3xl shadow-xl max-w-md text-center border border-gray-100">
          <div className="text-6xl mb-6">⚠️</div>
          <h2 className="text-2xl font-black text-gray-900 mb-2 tracking-tight">Analysis Failed</h2>
          <p className="text-gray-500 mb-8 font-medium">
            Something went wrong while analyzing your contract.
            Please try again or upload a different document.
          </p>

          <div className="flex gap-4 justify-center">
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 font-bold uppercase tracking-widest text-xs transition-colors shadow-lg shadow-indigo-100"
            >
              Retry
            </button>

            <button
              onClick={() => navigate("/")}
              className="px-6 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 font-bold uppercase tracking-widest text-xs transition-colors"
            >
              Start Over
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!results) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-indigo-200 border-t-indigo-600 mb-6"></div>
          <h2 className="text-2xl font-black text-gray-900 mb-2 tracking-tight animate-pulse">Analyzing Contract...</h2>
          <p className="text-gray-500 font-medium uppercase tracking-widest text-xs">{status?.filename}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-50/50">
      {showDisclaimer && (
        <div className="bg-amber-100 border-b border-amber-200 text-amber-900/80 px-4 py-2 text-[10px] font-bold text-center uppercase tracking-widest relative">
          ⚠️ AI-generated analysis. Not a substitute for professional legal counsel.
          <button
            onClick={() => setShowDisclaimer(false)}
            className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 flex items-center justify-center hover:bg-amber-200 rounded-full transition-colors group"
            aria-label="Close disclaimer"
          >
            <span className="text-amber-900/60 group-hover:text-amber-900 text-lg leading-none">×</span>
          </button>
        </div>
      )}

      <div className="flex-grow py-12 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-black text-gray-900 tracking-tighter">Contract Analysis</h1>
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 bg-white hover:bg-gray-50 text-gray-700 rounded-xl shadow-sm border border-gray-200 font-bold text-xs uppercase tracking-widest transition-all"
            >
              ← New Analysis
            </button>
          </div>

          <RiskSummary results={results} />

          {results.compound_risks.length > 0 && (
            <div className="bg-gradient-to-r from-orange-50 to-orange-100/50 border border-orange-200 p-8 mb-8 rounded-[2rem] shadow-sm">
              <h3 className="text-xl font-black text-orange-900 mb-6 uppercase tracking-tight flex items-center gap-3">
                <span className="text-2xl">⚠️</span> Compound Risks Detected
              </h3>
              {results.compound_risks.map((risk, i) => (
                <div key={i} className="mb-6 last:mb-0 bg-white/60 p-6 rounded-2xl border border-orange-100">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="font-black text-gray-900 tracking-tight">{risk.risk_type}</span>
                    <span className="px-3 py-1 bg-orange-200 text-orange-900 rounded-lg text-[10px] font-black uppercase tracking-widest">
                      {risk.severity}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mb-4 leading-relaxed font-medium">{risk.description}</p>
                  <p className="text-sm text-indigo-900/80 bg-indigo-50/50 p-4 rounded-xl border border-indigo-100/30 font-medium italic">
                    💡 <strong>Mitigation:</strong> {risk.mitigation}
                  </p>
                </div>
              ))}
            </div>
          )}

          <div>
            <div className="flex items-center gap-3 mb-6">
              <div className="h-8 w-1.5 bg-indigo-600 rounded-full"></div>
              <h2 className="text-2xl font-black text-gray-900 tracking-tight">Risky Clauses ({results.risky_clauses.length})</h2>
            </div>

            {results.risky_clauses.map((clause, i) => (
              <ClauseCard
                key={clause.chunk_id}
                clause={clause}
                index={i}
                analysisId={results.analysis_id}
              />
            ))}
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default AnalysisPage;