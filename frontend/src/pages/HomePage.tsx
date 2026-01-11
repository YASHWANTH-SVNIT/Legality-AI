import React from 'react';
import FileUploader from '../components/upload/FileUploader';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Legality AI
          </h1>
          <p className="text-xl text-gray-600">
            AI-Powered Contract Risk Analyzer
          </p>
          <p className="text-gray-500 mt-2">
            Upload your contract PDF and get instant risk analysis with AI-powered insights
          </p>
        </div>

        <FileUploader />

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-6 bg-white rounded-lg shadow-sm">
            <div className="text-3xl mb-2">🤖</div>
            <h3 className="font-semibold text-gray-900 mb-2">AI Agents</h3>
            <p className="text-sm text-gray-600">
              3 adversarial agents analyze every clause
            </p>
          </div>
          <div className="text-center p-6 bg-white rounded-lg shadow-sm">
            <div className="text-3xl mb-2">⚡</div>
            <h3 className="font-semibold text-gray-900 mb-2">Instant Results</h3>
            <p className="text-sm text-gray-600">
              Get analysis in under 60 seconds
            </p>
          </div>
          <div className="text-center p-6 bg-white rounded-lg shadow-sm">
            <div className="text-3xl mb-2">✨</div>
            <h3 className="font-semibold text-gray-900 mb-2">Smart Fixes</h3>
            <p className="text-sm text-gray-600">
              AI generates safe replacement clauses
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;