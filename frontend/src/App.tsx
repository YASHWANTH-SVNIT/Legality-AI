import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AnalysisPage from './pages/AnalysisPage';
import AdminPage from './pages/AdminPage';
import AdminLoginPage from './pages/AdminLoginPage';
import { checkHealth } from './services/api';

function App() {
  const [isBackendReady, setIsBackendReady] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    const checkBackend = async () => {
      const isHealthy = await checkHealth();
      if (isHealthy) {
        setIsBackendReady(true);
      } else {
        // Retry every 2 seconds
        setTimeout(() => setRetryCount(c => c + 1), 2000);
      }
    };

    checkBackend();
  }, [retryCount]);

  if (!isBackendReady) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
        <div className="bg-white p-12 rounded-[2.5rem] shadow-2xl border border-gray-100 max-w-lg w-full text-center relative overflow-hidden">

          {/* Decorative Background Blur */}
          <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"></div>
          <div className="absolute -top-20 -right-20 w-40 h-40 bg-purple-100 rounded-full blur-3xl opacity-50"></div>
          <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-indigo-100 rounded-full blur-3xl opacity-50"></div>

          <div className="relative z-10">
            <div className="mx-auto w-24 h-24 mb-8 relative">
              <div className="w-full h-full border-4 border-indigo-100 rounded-full"></div>
              <div className="absolute top-0 left-0 w-full h-full border-4 border-indigo-600 rounded-full animate-spin border-t-transparent"></div>
              <span className="absolute inset-0 flex items-center justify-center text-3xl">⚖️</span>
            </div>

            <h1 className="text-3xl font-black text-gray-900 mb-2 tracking-tight">Legality AI</h1>
            <h2 className="font-bold text-gray-400 mb-8 uppercase tracking-widest text-xs">System Initialization</h2>

            <div className="space-y-4">
              <div className="flex items-center gap-3 bg-gray-50 p-4 rounded-xl border border-gray-100">
                <span className="flex h-3 w-3 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
                </span>
                <span className="text-sm font-medium text-gray-600">Starting Neural Engines...</span>
              </div>
            </div>

            <p className="mt-8 text-xs text-gray-400 font-medium">
              Please ensure the backend server is running. <br />
              (<code className="bg-gray-100 px-1 py-0.5 rounded text-gray-600">python run.py</code>)
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/analysis/:analysisId" element={<AnalysisPage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/admin/login" element={<AdminLoginPage />} />
      </Routes>
    </Router>
  );
}

export default App;