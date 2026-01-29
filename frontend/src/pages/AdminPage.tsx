import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import FeedbackTable from '../components/admin/FeedbackTable';

const AdminPage: React.FC = () => {
    const [activeTab, setActiveTab] = useState('feedback');
    const navigate = useNavigate();

    useEffect(() => {
        if (!localStorage.getItem('adminKey')) {
            navigate('/admin/login');
        }
    }, [navigate]);

    return (
        <div className="min-h-screen bg-gray-50">
            <nav className="bg-white shadow">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex">
                            <div className="flex-shrink-0 flex items-center">
                                <span className="text-2xl mr-2">⚖️</span>
                                <h1 className="text-xl font-bold text-gray-900">Legality AI <span className="text-blue-600">Admin</span></h1>
                            </div>
                            <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
                                {[
                                    { id: 'feedback', label: 'User Feedback' }
                                ].map((tab) => (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className={`${activeTab === tab.id
                                            ? 'border-blue-500 text-gray-900'
                                            : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                                            } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                                    >
                                        {tab.label}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="flex items-center">
                            <a href="/" className="text-sm text-gray-500 hover:text-gray-900 mr-4">Back to App</a>
                            <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold">
                                A
                            </div>
                        </div>
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                {activeTab === 'feedback' && <FeedbackTable />}
            </main>
        </div>
    );
};

export default AdminPage;
