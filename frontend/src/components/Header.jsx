import React from 'react';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { Bell, Search, ChevronRight } from 'lucide-react';

export default function Header({ activeTab }) {
    const getBreadcrumb = () => {
        switch (activeTab) {
            case 'dashboard': return 'Portfolio Overview';
            case 'deploy': return 'Token Issuance';
            case 'token_manager': return 'Token Management';
            default: return activeTab.charAt(0).toUpperCase() + activeTab.slice(1);
        }
    };

    return (
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8 sticky top-0 z-40">
            {/* Breadcrumbs */}
            <div className="flex items-center text-sm text-gray-500">
                <span className="hover:text-gray-900 cursor-pointer transition-colors">Dashboard</span>
                <ChevronRight className="w-4 h-4 mx-2 text-gray-400" />
                <span className="font-medium text-gray-900">{getBreadcrumb()}</span>
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-4">
                {/* Search (Visual Only) */}
                <div className="relative hidden md:block">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search assets..."
                        className="pl-9 pr-4 py-1.5 text-sm border border-gray-200 rounded-full focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 w-64 transition-all"
                    />
                </div>

                {/* Notifications */}
                <button className="relative p-2 text-gray-400 hover:text-gray-600 transition-colors rounded-full hover:bg-gray-100">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
                </button>

                {/* Wallet Connection */}
                <div className="h-8 flex items-center">
                    <ConnectButton.Custom>
                        {({
                            account,
                            chain,
                            openAccountModal,
                            openChainModal,
                            openConnectModal,
                            authenticationStatus,
                            mounted,
                        }) => {
                            const ready = mounted && authenticationStatus !== 'loading';
                            const connected =
                                ready &&
                                account &&
                                chain &&
                                (!authenticationStatus ||
                                    authenticationStatus === 'authenticated');

                            return (
                                <div
                                    {...(!ready && {
                                        'aria-hidden': true,
                                        'style': {
                                            opacity: 0,
                                            pointerEvents: 'none',
                                            userSelect: 'none',
                                        },
                                    })}
                                >
                                    {(() => {
                                        if (!connected) {
                                            return (
                                                <button onClick={openConnectModal} type="button" className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-full transition-colors shadow-sm shadow-blue-200">
                                                    Connect Wallet
                                                </button>
                                            );
                                        }

                                        if (chain.unsupported) {
                                            return (
                                                <button onClick={openChainModal} type="button" className="bg-red-500 hover:bg-red-600 text-white text-sm font-medium px-4 py-2 rounded-full transition-colors">
                                                    Wrong network
                                                </button>
                                            );
                                        }

                                        return (
                                            <div className="flex items-center gap-2 bg-gray-50 rounded-full p-1 pr-4 border border-gray-200">
                                                <button
                                                    onClick={openChainModal}
                                                    className="flex items-center justify-center w-8 h-8 rounded-full bg-white shadow-sm border border-gray-100"
                                                >
                                                    {chain.hasIcon && (
                                                        <div
                                                            style={{
                                                                background: chain.iconBackground,
                                                                width: 20,
                                                                height: 20,
                                                                borderRadius: 999,
                                                                overflow: 'hidden',
                                                                marginRight: 0,
                                                            }}
                                                        >
                                                            {chain.iconUrl && (
                                                                <img
                                                                    alt={chain.name ?? 'Chain icon'}
                                                                    src={chain.iconUrl}
                                                                    style={{ width: 20, height: 20 }}
                                                                />
                                                            )}
                                                        </div>
                                                    )}
                                                </button>

                                                <button onClick={openAccountModal} type="button" className="text-sm font-medium text-gray-700 font-mono">
                                                    {account.displayName}
                                                    {account.displayBalance
                                                        ? ` (${account.displayBalance})`
                                                        : ''}
                                                </button>
                                            </div>
                                        );
                                    })()}
                                </div>
                            );
                        }}
                    </ConnectButton.Custom>
                </div>
            </div>
        </header>
    );
}
