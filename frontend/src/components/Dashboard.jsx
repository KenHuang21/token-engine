import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Plus } from 'lucide-react';
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

    if (isLoading) return <div>Loading...</div>;
    if (error) return <div className="text-red-500">Error loading portfolio</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold">Portfolio Overview</h1>
                <button
                    onClick={onDeploy}
                    className="bg-black text-white px-4 py-2 rounded flex items-center gap-2 hover:bg-gray-800"
                >
                    <Plus className="w-4 h-4" />
                    Deploy New Token
                </button>
            </div>

            <div className="border border-gray-300">
                <table className="w-full text-left border-collapse">
                    <thead className="bg-gray-100">
                        <tr>
                            <th className="border border-gray-300 px-4 py-2 text-sm font-semibold">Token</th>
                            <th className="border border-gray-300 px-4 py-2 text-sm font-semibold">Symbol</th>
                            <th className="border border-gray-300 px-4 py-2 text-sm font-semibold">Type</th>
                            <th className="border border-gray-300 px-4 py-2 text-sm font-semibold">Contract</th>
                            <th className="border border-gray-300 px-4 py-2 text-sm font-semibold">Chain</th>
                            <th className="border border-gray-300 px-4 py-2 text-sm font-semibold">Status</th>
                            <th className="border border-gray-300 px-4 py-2 text-sm font-semibold">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {contracts.map((c, i) => (
                            <tr key={i} className="hover:bg-gray-50">
                                <td className="border border-gray-300 px-4 py-2">{c.name}</td>
                                <td className="border border-gray-300 px-4 py-2">{c.symbol}</td>
                                <td className="border border-gray-300 px-4 py-2">{c.type}</td>
                                <td className="border border-gray-300 px-4 py-2 font-mono text-xs">
                                    {c.contract_address ? (
                                        <a
                                            href={getBlockExplorerUrl(c.chain_id, c.contract_address)}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-blue-600 hover:underline"
                                        >
                                            {c.contract_address}
                                        </a>
                                    ) : (
                                        '-'
                                    )}
                                </td>
                                <td className="border border-gray-300 px-4 py-2">{c.chain_id}</td>
                                <td className="border border-gray-300 px-4 py-2">{c.status}</td>
                                <td className="border border-gray-300 px-4 py-2">
                                    <button
                                        onClick={() => onSelectToken && onSelectToken(c)}
                                        className="text-blue-600 hover:underline text-sm"
                                    >
                                        Manage
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
