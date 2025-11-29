import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Plus, Coins, Wallet, Activity, ExternalLink } from 'lucide-react';
import axios from 'axios';
import { getBlockExplorerUrl } from '../utils';

const API_URL = '/api';

export default function Dashboard({ onSelectToken, onDeploy }) {
    const { data: contracts, isLoading, error } = useQuery({
        queryKey: ['tokens'],
        queryFn: async () => {
            const res = await axios.get(`${API_URL}/tokens`);
            return res.data;
        }
    });

    if (isLoading) return (
        <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
    );

    if (error) return (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            Error loading portfolio data. Please try again later.
        </div>
    );

    // Calculate stats
    const totalTokens = contracts?.length || 0;
    const deployedTokens = contracts?.filter(c => c.status === 'Deployed').length || 0;
    const pendingTokens = contracts?.filter(c => c.status === 'Pending').length || 0;

    const getStatusBadge = (status) => {
        switch (status) {
            case 'Deployed': return <span className="badge badge-success">Deployed</span>;
            case 'Pending': return <span className="badge badge-warning">Pending</span>;
            case 'Failed': return <span className="badge badge-error">Failed</span>;
            default: return <span className="badge badge-neutral">{status}</span>;
        }
    };

    return (
        <div className="space-y-8">
            {/* Page Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Portfolio Overview</h1>
                    <p className="text-slate-500 mt-1">Manage your tokenized assets across multiple chains.</p>
                </div>
                <button
                    onClick={onDeploy}
                    className="btn-primary"
                >
                    <Plus className="w-4 h-4 mr-2" />
                    Deploy New Token
                </button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="card p-6 flex items-center gap-4">
                    <div className="p-3 bg-indigo-50 rounded-full text-indigo-600">
                        <Coins className="w-6 h-6" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-slate-500">Total Assets</p>
                        <p className="text-2xl font-bold text-slate-900">{totalTokens}</p>
                    </div>
                </div>
                <div className="card p-6 flex items-center gap-4">
                    <div className="p-3 bg-emerald-50 rounded-full text-emerald-600">
                        <Activity className="w-6 h-6" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-slate-500">Active Deployments</p>
                        <p className="text-2xl font-bold text-slate-900">{deployedTokens}</p>
                    </div>
                </div>
                <div className="card p-6 flex items-center gap-4">
                    <div className="p-3 bg-amber-50 rounded-full text-amber-600">
                        <Wallet className="w-6 h-6" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-slate-500">Pending Actions</p>
                        <p className="text-2xl font-bold text-slate-900">{pendingTokens}</p>
                    </div>
                </div>
            </div>

            {/* Assets Table */}
            <div className="card">
                <div className="px-6 py-4 border-b border-slate-200">
                    <h2 className="text-lg font-semibold text-slate-900">Your Assets</h2>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-slate-50 border-b border-slate-200">
                            <tr>
                                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Token</th>
                                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Type</th>
                                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Contract</th>
                                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Chain</th>
                                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-200">
                            {contracts.length === 0 ? (
                                <tr>
                                    <td colSpan="6" className="px-6 py-12 text-center text-slate-500">
                                        No tokens found. Deploy your first token to get started.
                                    </td>
                                </tr>
                            ) : (
                                contracts.map((c, i) => (
                                    <tr key={i} className="hover:bg-slate-50 transition-colors">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center">
                                                <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold text-sm mr-3">
                                                    {c.symbol?.[0] || '?'}
                                                </div>
                                                <div>
                                                    <div className="font-medium text-slate-900">{c.name}</div>
                                                    <div className="text-sm text-slate-500">{c.symbol}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
                                                {c.type}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            {c.contract_address && c.contract_address !== 'Pending' ? (
                                                <a
                                                    href={getBlockExplorerUrl(c.chain_id, c.contract_address)}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="flex items-center text-sm text-indigo-600 hover:text-indigo-900 font-mono"
                                                >
                                                    {c.contract_address.slice(0, 6)}...{c.contract_address.slice(-4)}
                                                    <ExternalLink className="w-3 h-3 ml-1" />
                                                </a>
                                            ) : (
                                                <span className="text-sm text-slate-400 font-mono">-</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="text-sm text-slate-900">{c.chain_id}</div>
                                        </td>
                                        <td className="px-6 py-4">
                                            {getStatusBadge(c.status)}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <button
                                                onClick={() => onSelectToken && onSelectToken(c)}
                                                className="btn-secondary text-xs py-1.5"
                                                disabled={c.status !== 'Deployed'}
                                            >
                                                Manage
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
