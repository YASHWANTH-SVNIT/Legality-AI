import { useState, useEffect } from 'react';
import { getAnalysisStatus, getAnalysisResults } from '../services/api';
import { AnalysisStatus, AnalysisResults } from '../types';

export const useAnalysis = (analysisId: string) => {
  const [status, setStatus] = useState<AnalysisStatus | null>(null);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const pollStatus = async () => {
      try {
        const statusData = await getAnalysisStatus(analysisId);
        setStatus(statusData);

        if (statusData.status === 'completed') {
          const resultsData = await getAnalysisResults(analysisId);
          setResults(resultsData);
          clearInterval(interval);
        } else if (statusData.status === 'failed') {
          setError('Analysis failed');
          clearInterval(interval);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to fetch status');
        clearInterval(interval);
      }
    };

    pollStatus();
    interval = setInterval(pollStatus, 2000);

    return () => clearInterval(interval);
  }, [analysisId]);

  return { status, results, error };
};