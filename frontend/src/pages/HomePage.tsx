import React from 'react';
import FileUploader from '../components/upload/FileUploader';
import Footer from '../components/common/Footer';

const HomePage: React.FC = () => {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50/50">
      <div className="flex-grow py-20 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16 space-y-6">
            <div className="inline-block p-4 bg-white rounded-3xl shadow-sm border border-gray-100 mb-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <span className="text-4xl">⚖️</span>
            </div>
            <h1 className="text-6xl font-black text-gray-900 tracking-tighter mb-4 bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600">
              Legality AI
            </h1>
            <p className="text-2xl font-light text-gray-500 max-w-2xl mx-auto leading-relaxed">
              The adversarial AI watchdog for your legal contracts.
            </p>
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-full text-xs font-bold uppercase tracking-widest border border-indigo-100">
              <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
              RAG 2.0 Active
            </div>
          </div>

          <div className="bg-white p-2 rounded-[2.5rem] shadow-xl shadow-gray-200/50 border border-white/50 backdrop-blur-sm">
            <FileUploader />
          </div>

          <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="group p-8 bg-white rounded-[2rem] border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
              <div className="text-4xl mb-6 bg-rose-50 w-16 h-16 flex items-center justify-center rounded-2xl group-hover:scale-110 transition-transform">🤖</div>
              <h3 className="text-lg font-black text-gray-900 mb-3 tracking-tight">Debate Loop AI</h3>
              <p className="text-sm font-medium text-gray-400 leading-relaxed">
                Three rival AI agents (Pessimist, Optimist, Arbiter) argue over every clause to ensure zero hallucinations.
              </p>
            </div>
            <div className="group p-8 bg-white rounded-[2rem] border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
              <div className="text-4xl mb-6 bg-amber-50 w-16 h-16 flex items-center justify-center rounded-2xl group-hover:scale-110 transition-transform">⚡</div>
              <h3 className="text-lg font-black text-gray-900 mb-3 tracking-tight">OCR & Scan Ready</h3>
              <p className="text-sm font-medium text-gray-400 leading-relaxed">
                Upload scanned PDFs or images. Our engine automatically extracts text, cleans noise, and analyzes risk.
              </p>
            </div>
            <div className="group p-8 bg-white rounded-[2rem] border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
              <div className="text-4xl mb-6 bg-emerald-50 w-16 h-16 flex items-center justify-center rounded-2xl group-hover:scale-110 transition-transform">✨</div>
              <h3 className="text-lg font-black text-gray-900 mb-3 tracking-tight">Interactive Knowledge</h3>
              <p className="text-sm font-medium text-gray-400 leading-relaxed">
                Flag false positives to train the system. Your feedback directly improves the Vector DB in real-time.
              </p>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default HomePage;