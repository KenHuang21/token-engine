import React from 'react';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { LayoutDashboard, PlusCircle, FileText } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
    return (
        <aside className="w-64 bg-white border-r border-gray-300 flex flex-col h-screen">
            {/* Header */}
            <div className="h-16 flex items-center px-4 border-b border-gray-300">
                <div className="flex items-center gap-2">
                    <FileText className="w-6 h-6" />
                    <span className="text-xl font-bold text-black">TokenEngine</span>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 py-6 px-2 space-y-1">
                <button
                    onClick={() => setActiveTab('dashboard')}
                    className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md ${activeTab === 'dashboard' ? 'bg-gray-100 text-black' : 'text-gray-600 hover:bg-gray-50'
                        }`}
                >
                    <LayoutDashboard className="w-5 h-5" />
                    Portfolio
                </button>
                <button
                    onClick={() => setActiveTab('deploy')}
                    className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md ${activeTab === 'deploy' ? 'bg-gray-100 text-black' : 'text-gray-600 hover:bg-gray-50'
                        }`}
                >
                    <PlusCircle className="w-5 h-5" />
                    Deploy Token
                </button>
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-gray-300">
                <p className="text-xs font-bold text-gray-500 uppercase mb-2">Connected Wallet</p>
                <ConnectButton showBalance={false} accountStatus="address" chainStatus="icon" />
            </div>
        </aside>
    );
}
