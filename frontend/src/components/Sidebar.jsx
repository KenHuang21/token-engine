import React from 'react';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { LayoutDashboard, PlusCircle, FileText } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
    return (
        <aside className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen sticky top-0">
            {/* Header */}
            <div className="h-16 flex items-center px-6 border-b border-slate-200">
                <div className="flex items-center gap-2 text-indigo-600">
                    <FileText className="w-6 h-6" />
                    <span className="text-xl font-bold text-slate-900">TokenEngine</span>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 py-6 px-3 space-y-1">
                <button
                    onClick={() => setActiveTab('dashboard')}
                    className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${activeTab === 'dashboard'
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                        }`}
                >
                    <LayoutDashboard className={`w-5 h-5 ${activeTab === 'dashboard' ? 'text-indigo-600' : 'text-slate-400'}`} />
                    Portfolio
                </button>
                <button
                    onClick={() => setActiveTab('deploy')}
                    className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${activeTab === 'deploy'
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                        }`}
                >
                    <PlusCircle className={`w-5 h-5 ${activeTab === 'deploy' ? 'text-indigo-600' : 'text-slate-400'}`} />
                    Deploy Token
                </button>
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-slate-200 bg-slate-50">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Connected Wallet</p>
                <ConnectButton showBalance={false} accountStatus="address" chainStatus="icon" />
            </div>
        </aside>
    );
}
