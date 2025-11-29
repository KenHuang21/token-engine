import { useState, useEffect } from 'react';
import { useWalletClient, usePublicClient } from 'wagmi';
import { parseEther, pad, toHex } from 'viem';
import axios from 'axios';
import { sha256 } from 'js-sha256';
import { ExternalLink, ArrowLeft } from 'lucide-react';
import { getBlockExplorerUrl } from '../utils';
import ErrorDisplay from './ErrorDisplay';

const API_URL = '/api';

export default function TokenManager({ token, onBack }) {
    const [activeTab, setActiveTab] = useState('holders'); // Default to holders as per screenshot
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

    return (
        <div className="space-y-4">
            <button onClick={onBack} className="border border-gray-400 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200">
                ← Back to Dashboard
            </button>

            <div className="border border-black p-4 bg-white">
                <div className="flex justify-between items-start">
                    <div>
                        <h2 className="text-xl font-bold">{token.name} ({token.symbol})</h2>
                        <div className="text-sm mt-1">
                            {token.chain_id} • {token.status}
                        </div>
                        <div className="text-sm font-mono mt-1 flex items-center gap-1">
                            Contract:
                            <a
                                href={getBlockExplorerUrl(token.chain_id, token.contract_address)}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:underline flex items-center gap-1"
                            >
                                {token.contract_address}
                                <ExternalLink className="w-3 h-3" />
                            </a>
                        </div>
                    </div>
                    <div className="text-right">
                        <span className="border border-black px-2 py-1 text-xs font-bold uppercase">
                            {token.type}
                        </span>
                    </div>
                </div>

                <div className="mt-6 border border-black flex">
                    {['mint', 'holders', 'docs'].map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`flex-1 py-2 text-center font-bold border-r border-black last:border-r-0 ${activeTab === tab ? 'bg-gray-200' : 'hover:bg-gray-50'
                                }`}
                        >
                            {tab === 'mint' ? 'Minting' : tab === 'holders' ? 'Holders' : 'Documents'}
                        </button>
                    ))}
                </div>

                <div className="mt-4">
                    {activeTab === 'mint' && (
                        <div className="max-w-lg">
                            <h3 className="font-bold mb-4">Mint New Tokens</h3>
                            <ErrorDisplay error={error} onDismiss={() => setError(null)} />

                            <form onSubmit={handleMint} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-bold mb-1">Partition</label>
                                    <select
                                        value={mintData.partition}
                                        onChange={(e) => setMintData({ ...mintData, partition: e.target.value })}
                                        className="w-full border border-black p-2"
                                    >
                                        {token.partitions.map(p => (
                                            <option key={p} value={p}>{p}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-bold mb-1">Recipient</label>
                                    <input
                                        type="text"
                                        value={mintData.to}
                                        onChange={(e) => setMintData({ ...mintData, to: e.target.value })}
                                        className="w-full border border-black p-2 font-mono"
                                        placeholder="0x..."
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-bold mb-1">Amount</label>
                                    <input
                                        type="number"
                                        value={mintData.amount}
                                        onChange={(e) => setMintData({ ...mintData, amount: parseInt(e.target.value) })}
                                        className="w-full border border-black p-2"
                                    />
                                </div>
                                <button type="submit" disabled={loading} className="bg-black text-white px-4 py-2 font-bold">
                                    {loading ? 'Minting...' : 'Mint Tokens'}
                                </button>
                            </form>
                        </div>
                    )}

                    {activeTab === 'holders' && (
                        <div>
                            <div className="flex justify-between items-center mb-4">
                                <h3 className="font-bold">Token Holders</h3>
                                <button onClick={fetchHolders} className="border border-black px-2 py-1 text-xs">
                                    Refresh
                                </button>
                            </div>
                            <table className="w-full border-collapse border border-black">
                                <thead className="bg-gray-100">
                                    <tr>
                                        <th className="border border-black px-4 py-2 text-left text-xs uppercase">Address</th>
                                        <th className="border border-black px-4 py-2 text-left text-xs uppercase">Tranche</th>
                                        <th className="border border-black px-4 py-2 text-right text-xs uppercase">Balance</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {holders.map((h, i) => (
                                        <tr key={i}>
                                            <td className="border border-black px-4 py-2 font-mono text-sm">
                                                <a
                                                    href={getBlockExplorerUrl(token.chain_id, h.address)}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="text-blue-600 hover:underline"
                                                >
                                                    {h.address}
                                                </a>
                                            </td>
                                            <td className="border border-black px-4 py-2 text-sm">{h.partition}</td>
                                            <td className="border border-black px-4 py-2 text-right text-sm">{h.balance}</td>
                                        </tr>
                                    ))}
                                    {holders.length === 0 && (
                                        <tr>
                                            <td colSpan="3" className="border border-black px-4 py-8 text-center text-gray-500">
                                                No holders found.
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}

                    {activeTab === 'docs' && (
                        <div className="max-w-lg">
                            <h3 className="font-bold mb-4">Upload Document</h3>
                            <form onSubmit={handleDocSubmit} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-bold mb-1">Name</label>
                                    <input
                                        type="text"
                                        value={docData.name}
                                        onChange={(e) => setDocData({ ...docData, name: e.target.value })}
                                        className="w-full border border-black p-2"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-bold mb-1">URI</label>
                                    <input
                                        type="url"
                                        value={docData.uri}
                                        onChange={(e) => setDocData({ ...docData, uri: e.target.value })}
                                        className="w-full border border-black p-2"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-bold mb-1">Hash</label>
                                    <input
                                        type="file"
                                        onChange={handleFileUpload}
                                        className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:border file:border-black file:text-sm file:font-semibold file:bg-gray-50 file:text-black hover:file:bg-gray-100"
                                    />
                                    {docData.hash && <div className="mt-1 text-xs font-mono">{docData.hash}</div>}
                                </div>
                                <button type="submit" disabled={loading} className="bg-black text-white px-4 py-2 font-bold">
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
