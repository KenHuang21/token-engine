import React from 'react';
import Sidebar from './Sidebar';

export default function DashboardLayout({ children, activeTab, setActiveTab }) {
    return (
        <div className="flex min-h-screen bg-slate-50">
            <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
            <main className="flex-1 overflow-auto p-8">
                {children}
            </main>
        </div>
    );
}
