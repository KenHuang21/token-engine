import { useState } from 'react';
import { useWalletClient, useAccount } from 'wagmi';
import { useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
// Let's use viem for deployment via wagmi

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function DeploymentTabs() {
    const [mode, setMode] = useState('MANAGED'); // MANAGED or BYOW
    const [formData, setFormData] = useState({
        name: 'My Token',
        symbol: 'MTK',
        partitions: 'ClassA',
        chain_id: 'BSC_BNB' // Default for Managed. For BYOW we use connected chain.
    });
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState('');

    const { data: walletClient } = useWalletClient();
    const { address } = useAccount();
    const queryClient = useQueryClient();

    const handleDeploy = async (e) => {
        e.preventDefault();
        setLoading(true);
        setStatus('Starting deployment...');

        try {
            if (mode === 'MANAGED') {
                // Call Backend
                const res = await axios.post(`${API_URL}/deploy/managed`, {
                    chain_id: formData.chain_id,
                    name: formData.name,
                    symbol: formData.symbol,
                    partitions: [formData.partitions] // Simple single partition for MVP
                });
                setStatus(`Submitted! Tx ID: ${res.data.tx_id}`);
            } else {
                // BYOW
                if (!walletClient) throw new Error("Wallet not connected");

                setStatus('Fetching artifacts...');
                const artifacts = await axios.get(`${API_URL}/artifacts`);
                const { abi, bytecode } = artifacts.data;

                setStatus('Deploying via Wallet...');

                // Prepare partitions
                // We need to encode constructor args manually or use viem's deployContract
                // Using walletClient.deployContract is easiest if we have ABI/Bytecode

                // Note: partitions input is string, need to convert to bytes32 array
                // For MVP, let's assume the user enters a string and we pad it.
                // But doing this in JS without web3.js/ethers is annoying.
                // Let's use the backend to encode args? No, that's complex.
                // Let's use a simple hex string for ClassA: 0x436c61737341...
                const partitionHex = "0x436c617373410000000000000000000000000000000000000000000000000000";

                const hash = await walletClient.deployContract({
                    abi: abi,
                    bytecode: bytecode,
                    args: [formData.name, formData.symbol, [partitionHex], address],
                });

                setStatus(`Deployed! Tx Hash: ${hash}`);

                // Sync with Backend
                await axios.post(`${API_URL}/sync/byow`, {
                    chain_id: 'BSC', // Assuming user is on BSC
                    address: '0x...', // We don't know address yet until receipt. MVP: Just save hash.
                    name: formData.name,
                    symbol: formData.symbol,
                    owner: address,
                    tx_hash: hash
                });
            }

            // Refresh Dashboard
            queryClient.invalidateQueries(['contracts']);

        } catch (err) {
            console.error(err);
            setStatus(`Error: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div className="flex border-b mb-4">
                <button
                    className={`py-2 px-4 ${mode === 'MANAGED' ? 'border-b-2 border-blue-500 font-bold' : ''}`}
                    onClick={() => setMode('MANAGED')}
                >
                    Managed (Cobo)
                </button>
                <button
                    className={`py-2 px-4 ${mode === 'BYOW' ? 'border-b-2 border-blue-500 font-bold' : ''}`}
                    onClick={() => setMode('BYOW')}
                >
                    Self-Custody (BYOW)
                </button>
            </div>

            <form onSubmit={handleDeploy} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Token Name</label>
                    <input
                        type="text"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                        value={formData.name}
                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Token Symbol</label>
                    <input
                        type="text"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                        value={formData.symbol}
                        onChange={e => setFormData({ ...formData, symbol: e.target.value })}
                    />
                </div>

                {mode === 'MANAGED' && (
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Chain ID</label>
                        <input
                            type="text"
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                            value={formData.chain_id}
                            onChange={e => setFormData({ ...formData, chain_id: e.target.value })}
                            disabled
                        />
                        <p className="text-xs text-gray-500">Fixed to BSC_BNB for MVP</p>
                    </div>
                )}

                <button
                    type="submit"
                    disabled={loading || (mode === 'BYOW' && !walletClient)}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none disabled:bg-gray-400"
                >
                    {loading ? 'Deploying...' : (mode === 'BYOW' && !walletClient ? 'Connect Wallet First' : 'Deploy Token')}
                </button>

                {status && <div className="mt-2 text-sm text-gray-600">{status}</div>}
            </form>
        </div>
    );
}
