import { useState, useEffect } from 'react';
import { useWalletClient, usePublicClient } from 'wagmi';
import { parseEther, pad, toHex } from 'viem';
import axios from 'axios';
import { sha256 } from 'js-sha256';
import { ExternalLink, ArrowLeft, Users, Coins, FileText, Upload, RefreshCw } from 'lucide-react';
import { getBlockExplorerUrl } from '../utils';
import ErrorDisplay from './ErrorDisplay';
import clsx from 'clsx';

const API_URL = '/api';

export default function TokenManager({ token, onBack }) {
    const [activeTab, setActiveTab] = useState('holders');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [holders, setHolders] = useState([]);
    const { data: walletClient } = useWalletClient();
    const publicClient = usePublicClient();

    // Mint Form
    const [mintData, setMintData] = useState({
        partition: token.partitions[0] || '',
        to: '',
        amount: 0
    });

    // Doc Form
    const [docData, setDocData] = useState({
        name: '',
        uri: '',
        hash: ''
    });

    // Fetch Holders
    useEffect(() => {
        if (activeTab === 'holders') {
            fetchHolders();
        }
    }, [activeTab]);

    const fetchHolders = async () => {
        try {
            const address = token.contract_address || token.owner;
            if (!address) return;
            const res = await axios.get(`${API_URL}/tokens/${token.chain_id}/${address}/holders`);
            setHolders(res.data);
        } catch (err) {
            console.error("Failed to fetch holders", err);
        }
    };

    const handleMint = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            if (token.type === 'SELF_CUSTODY') {
                if (!walletClient) throw new Error("Wallet not connected");

                // Get ABI
                const artifacts = await axios.get(`${API_URL}/artifacts`);
                const { abi } = artifacts.data;

                // Prepare args
                const partitionBytes = pad(toHex(mintData.partition), { size: 32, dir: 'right' });
                const amountWei = parseEther(mintData.amount.toString());

                // Send TX
                const hash = await walletClient.writeContract({
                    address: token.contract_address,
                    abi: abi,
                    functionName: 'issueByPartition',
                    args: [partitionBytes, mintData.to, amountWei, '0x']
                });

                alert(`Mint TX Sent! Waiting for confirmation... Tx: ${hash}`);

                // Wait for receipt
                await publicClient.waitForTransactionReceipt({ hash });

                // Register mint with backend for history/holders
                await axios.post(`${API_URL}/tokens/mint/register`, {
                    chain_id: token.chain_id,
                    contract_address: token.contract_address,
                    partition: mintData.partition,
                    to_address: mintData.to,
                    amount: Number(mintData.amount),
                    tx_hash: hash
                });

                alert("Minting Confirmed & Registered!");
            } else {
                // MANAGED
                await axios.post(`${API_URL}/tokens/mint`, {
                    chain_id: token.chain_id,
                    contract_address: token.contract_address || token.owner,
                    partition: mintData.partition,
                    to_address: mintData.to,
                    amount: Number(mintData.amount)
                });
                alert("Minting Submitted!");
            }
            setMintData({ ...mintData, amount: 0, to: '' });
            if (activeTab === 'holders') fetchHolders();
        } catch (err) {
            console.error('Minting error:', err);
            setError({
                message: err.response?.data?.detail || err.message || 'Failed to mint tokens',
                detail: err.response?.data?.error_type ? `Error Type: ${err.response.data.error_type}` : null
            });
        } finally {
            setLoading(false);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            const hash = sha256(event.target.result);
            setDocData(prev => ({ ...prev, hash: '0x' + hash }));
        };
        reader.readAsArrayBuffer(file);
    };

    const handleDocSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await axios.post(`${API_URL}/tokens/document`, {
                chain_id: token.chain_id,
                contract_address: token.contract_address || token.owner,
                name: docData.name,
                uri: docData.uri,
                hash: docData.hash
            });
            alert("Document Linked!");
            setDocData({ name: '', uri: '', hash: '' });
        } catch (err) {
            alert(`Error: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const tabs = [
        { id: 'holders', label: 'Holders', icon: Users },
        { id: 'mint', label: 'Minting', icon: Coins },
        { id: 'docs', label: 'Documents', icon: FileText },
    ];

    return (
        <div className="space-y-6">
            <button onClick={onBack} className="flex items-center text-sm text-slate-500 hover:text-indigo-600 transition-colors">
                <ArrowLeft className="w-4 h-4 mr-1" /> Back to Dashboard
            </button>

            <div className="card">
                <div className="p-6 border-b border-slate-200">
                    <div className="flex justify-between items-start">
                        <div>
                            <h2 className="text-2xl font-bold text-slate-900">{token.name} <span className="text-slate-400 font-normal">({token.symbol})</span></h2>
                            <div className="flex items-center gap-3 mt-2 text-sm">
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
                                    {token.chain_id}
                                </span>
                                <span className={clsx(
                                    "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                                    token.status === 'Deployed' ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"
                                )}>
                                    {token.status}
                                </span>
                                <div className="flex items-center gap-1 text-slate-500 font-mono">
                                    {token.contract_address}
                                    <a
                                        href={getBlockExplorerUrl(token.chain_id, token.contract_address)}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-indigo-600 hover:text-indigo-800"
                                    >
                                        <ExternalLink className="w-3 h-3" />
                                    </a>
                                </div>
                            </div>
                        </div>
                        <div className="text-right">
                            <span className="inline-flex items-center px-3 py-1 rounded-lg text-xs font-bold uppercase tracking-wider bg-slate-900 text-white">
                                {token.type.replace('_', ' ')}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="border-b border-slate-200">
                    <nav className="flex -mb-px px-6 gap-6" aria-label="Tabs">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={clsx(
                                    "group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors",
                                    activeTab === tab.id
                                        ? "border-indigo-600 text-indigo-600"
                                        : "border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300"
                                )}
                            >
                                <tab.icon className={clsx(
                                    "mr-2 h-4 w-4",
                                    activeTab === tab.id ? "text-indigo-600" : "text-slate-400 group-hover:text-slate-500"
                                )} />
                                {tab.label}
                            </button>
                        ))}
                    </nav>
                </div>

                <div className="p-6">
                    <ErrorDisplay error={error} onDismiss={() => setError(null)} />

                    {activeTab === 'mint' && (
                        <div className="max-w-xl mx-auto">
                            <div className="text-center mb-8">
                                <h3 className="text-lg font-medium text-slate-900">Mint New Tokens</h3>
                                <p className="text-sm text-slate-500">Issue new tokens to a specific wallet address.</p>
                            </div>

                            <form onSubmit={handleMint} className="space-y-6">
                                <div>
                                    <label className="label">Tranche / Partition</label>
                                    <select
                                        value={mintData.partition}
                                        onChange={(e) => setMintData({ ...mintData, partition: e.target.value })}
                                        className="input-field"
                                    >
                                        {token.partitions.map(p => (
                                            <option key={p} value={p}>{p}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="label">Recipient Address</label>
                                    <input
                                        type="text"
                                        value={mintData.to}
                                        onChange={(e) => setMintData({ ...mintData, to: e.target.value })}
                                        className="input-field font-mono"
                                        placeholder="0x..."
                                    />
                                </div>
                                <div>
                                    <label className="label">Amount</label>
                                    <div className="relative rounded-md shadow-sm">
                                        <input
                                            type="number"
                                            value={mintData.amount}
                                            onChange={(e) => setMintData({ ...mintData, amount: parseInt(e.target.value) })}
                                            className="input-field pr-12"
                                            placeholder="0"
                                        />
                                        <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                                            <span className="text-slate-500 sm:text-sm">{token.symbol}</span>
                                        </div>
                                    </div>
                                </div>
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full btn-primary py-3"
                                >
                                    {loading ? 'Processing...' : 'Mint Tokens'}
                                </button>
                            </form>
                        </div>
                    )}

                    {activeTab === 'holders' && (
                        <div>
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-lg font-medium text-slate-900">Token Holders</h3>
                                <button onClick={fetchHolders} className="btn-secondary text-xs">
                                    <RefreshCw className="w-3 h-3 mr-1.5" /> Refresh
                                </button>
                            </div>

                            <div className="overflow-hidden rounded-lg border border-slate-200">
                                <table className="min-w-full divide-y divide-slate-200">
                                    <thead className="bg-slate-50">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Address</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Tranche</th>
                                            <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Balance</th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-slate-200">
                                        {holders.map((h, i) => (
                                            <tr key={i} className="hover:bg-slate-50">
                                                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-indigo-600">
                                                    <a
                                                        href={getBlockExplorerUrl(token.chain_id, h.address)}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="hover:underline"
                                                    >
                                                        {h.address}
                                                    </a>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
                                                        {h.partition}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900 text-right font-medium">
                                                    {h.balance} {token.symbol}
                                                </td>
                                            </tr>
                                        ))}
                                        {holders.length === 0 && (
                                            <tr>
                                                <td colSpan="3" className="px-6 py-12 text-center text-slate-500">
                                                    No holders found.
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {activeTab === 'docs' && (
                        <div className="max-w-xl mx-auto">
                            <div className="text-center mb-8">
                                <h3 className="text-lg font-medium text-slate-900">Upload Document</h3>
                                <p className="text-sm text-slate-500">Attach legal documents or whitepapers to this asset.</p>
                            </div>

                            <form onSubmit={handleDocSubmit} className="space-y-6">
                                <div>
                                    <label className="label">Document Name</label>
                                    <input
                                        type="text"
                                        value={docData.name}
                                        onChange={(e) => setDocData({ ...docData, name: e.target.value })}
                                        className="input-field"
                                        placeholder="e.g. Offering Memorandum"
                                    />
                                </div>
                                <div>
                                    <label className="label">Document URI</label>
                                    <input
                                        type="url"
                                        value={docData.uri}
                                        onChange={(e) => setDocData({ ...docData, uri: e.target.value })}
                                        className="input-field"
                                        placeholder="https://..."
                                    />
                                </div>
                                <div>
                                    <label className="label">Document Hash</label>
                                    <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-slate-300 border-dashed rounded-lg hover:border-indigo-500 transition-colors cursor-pointer relative">
                                        <div className="space-y-1 text-center">
                                            <Upload className="mx-auto h-12 w-12 text-slate-400" />
                                            <div className="flex text-sm text-slate-600">
                                                <label htmlFor="file-upload" className="relative cursor-pointer rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none">
                                                    <span>Upload a file</span>
                                                    <input id="file-upload" name="file-upload" type="file" className="sr-only" onChange={handleFileUpload} />
                                                </label>
                                                <p className="pl-1">to generate hash</p>
                                            </div>
                                            <p className="text-xs text-slate-500">PDF, DOCX up to 10MB</p>
                                        </div>
                                    </div>
                                    {docData.hash && (
                                        <div className="mt-2 p-2 bg-slate-50 rounded text-xs font-mono text-slate-600 break-all border border-slate-200">
                                            Hash: {docData.hash}
                                        </div>
                                    )}
                                </div>
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full btn-primary py-3"
                                >
                                    Attach Document
                                </button>
                            </form>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
