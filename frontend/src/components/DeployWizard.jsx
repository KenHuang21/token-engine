import { useState } from 'react';
import { useWalletClient, useAccount } from 'wagmi';
import { useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { ChevronRight, Check, Plus, Trash2, Loader2, Layers, FileText, ShieldCheck } from 'lucide-react';
import clsx from 'clsx';

const API_URL = '/api';

export default function DeployWizard({ onComplete }) {
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [mode, setMode] = useState('MANAGED'); // MANAGED or BYOW

    const [formData, setFormData] = useState({
        name: '',
        symbol: '',
        supply: 0,
        partitions: ['Class A'] // Default partition
    });

    const { data: walletClient } = useWalletClient();
    const { address } = useAccount();
    const queryClient = useQueryClient();

    const addPartition = () => {
        setFormData(prev => ({ ...prev, partitions: [...prev.partitions, ''] }));
    };

    const removePartition = (index) => {
        setFormData(prev => ({
            ...prev,
            partitions: prev.partitions.filter((_, i) => i !== index)
        }));
    };

    const updatePartition = (index, value) => {
        const newPartitions = [...formData.partitions];
        newPartitions[index] = value;
        setFormData(prev => ({ ...prev, partitions: newPartitions }));
    };

    const handleDeploy = async () => {
        setLoading(true);
        try {
            const validPartitions = formData.partitions.filter(p => p.trim() !== '');

            if (mode === 'MANAGED') {
                const res = await axios.post(`${API_URL}/tokens/deploy`, {
                    chain_id: 'BSC_BNB',
                    name: formData.name,
                    symbol: formData.symbol,
                    partitions: validPartitions,
                    supply: Number(formData.supply)
                });
                alert(`Deployment Submitted! Tx ID: ${res.data.tx_id}`);
            } else {
                if (!walletClient) throw new Error("Wallet not connected");

                const artifacts = await axios.get(`${API_URL}/artifacts`);
                const { abi, bytecode } = artifacts.data;

                const padBytes32 = (str) => {
                    let hex = '';
                    for (let i = 0; i < str.length; i++) {
                        hex += str.charCodeAt(i).toString(16);
                    }
                    return '0x' + hex.padEnd(64, '0');
                };

                const partitionsBytes = validPartitions.map(p => padBytes32(p));

                const hash = await walletClient.deployContract({
                    abi: abi,
                    bytecode: bytecode,
                    args: [formData.name, formData.symbol, partitionsBytes, address],
                });

                // Note: Sync logic omitted for brevity as per previous context
                alert(`Deployed via Wallet! Tx: ${hash}`);
            }

            queryClient.invalidateQueries(['tokens']);
            onComplete();
        } catch (err) {
            console.error(err);
            alert(`Error: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const steps = [
        { id: 1, title: 'Asset Details', icon: FileText },
        { id: 2, title: 'Capital Structure', icon: Layers },
        { id: 3, title: 'Review & Sign', icon: ShieldCheck },
    ];

    return (
        <div className="max-w-3xl mx-auto">
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-gray-900">Issue New Security Token</h1>
                <p className="text-gray-500 mt-1">Configure your asset parameters and capital structure.</p>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                {/* Steps Header */}
                <div className="grid grid-cols-3 border-b border-gray-100">
                    {steps.map((s, i) => (
                        <div key={s.id} className={clsx(
                            "py-4 px-6 flex items-center gap-3 border-b-2 transition-colors",
                            step === s.id
                                ? "border-blue-600 bg-blue-50/50"
                                : "border-transparent hover:bg-gray-50",
                            step > s.id && "text-green-600"
                        )}>
                            <div className={clsx(
                                "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors",
                                step === s.id ? "bg-blue-600 text-white" :
                                    step > s.id ? "bg-green-100 text-green-600" : "bg-gray-100 text-gray-500"
                            )}>
                                {step > s.id ? <Check className="w-4 h-4" /> : s.id}
                            </div>
                            <div className={clsx(
                                "text-sm font-medium",
                                step === s.id ? "text-blue-900" : "text-gray-500"
                            )}>
                                {s.title}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="p-8">
                    {/* Step 1: Basics */}
                    {step === 1 && (
                        <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-3">Custody Model</label>
                                <div className="grid grid-cols-2 gap-4">
                                    <button
                                        type="button"
                                        onClick={() => setMode('MANAGED')}
                                        className={clsx(
                                            "p-4 rounded-xl border-2 text-left transition-all",
                                            mode === 'MANAGED'
                                                ? "border-blue-600 bg-blue-50 ring-1 ring-blue-600"
                                                : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                                        )}
                                    >
                                        <div className="font-semibold text-gray-900">Managed Custody</div>
                                        <div className="text-sm text-gray-500 mt-1">Keys managed by Cobo WaaS MPC. Best for institutions.</div>
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setMode('BYOW')}
                                        className={clsx(
                                            "p-4 rounded-xl border-2 text-left transition-all",
                                            mode === 'BYOW'
                                                ? "border-blue-600 bg-blue-50 ring-1 ring-blue-600"
                                                : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                                        )}
                                    >
                                        <div className="font-semibold text-gray-900">Self-Custody</div>
                                        <div className="text-sm text-gray-500 mt-1">Deploy using your connected wallet (Metamask, etc).</div>
                                    </button>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Token Name</label>
                                    <input
                                        type="text"
                                        className="input-field"
                                        value={formData.name}
                                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                                        placeholder="e.g. Real Estate Fund I"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Token Symbol</label>
                                    <input
                                        type="text"
                                        className="input-field"
                                        value={formData.symbol}
                                        onChange={e => setFormData({ ...formData, symbol: e.target.value })}
                                        placeholder="e.g. REFI"
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Step 2: Partitions */}
                    {step === 2 && (
                        <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                            <div className="flex justify-between items-center">
                                <div>
                                    <h3 className="text-lg font-medium text-gray-900">Tranches & Classes</h3>
                                    <p className="text-sm text-gray-500">Define the capital structure of your asset.</p>
                                </div>
                                <button onClick={addPartition} className="btn-secondary text-sm">
                                    <Plus className="w-4 h-4 mr-2" /> Add Tranche
                                </button>
                            </div>

                            <div className="space-y-3">
                                {formData.partitions.map((p, i) => (
                                    <div key={i} className="flex gap-3">
                                        <div className="flex-1">
                                            <input
                                                type="text"
                                                className="input-field"
                                                value={p}
                                                onChange={e => updatePartition(i, e.target.value)}
                                                placeholder={`Tranche ${i + 1} Name (e.g. Class ${String.fromCharCode(65 + i)})`}
                                            />
                                        </div>
                                        {formData.partitions.length > 1 && (
                                            <button
                                                onClick={() => removePartition(i)}
                                                className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                            >
                                                <Trash2 className="w-5 h-5" />
                                            </button>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Step 3: Review */}
                    {step === 3 && (
                        <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                            <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                                <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">Deployment Summary</h3>
                                <dl className="grid grid-cols-2 gap-x-4 gap-y-6">
                                    <div>
                                        <dt className="text-sm text-gray-500">Custody Model</dt>
                                        <dd className="mt-1 text-sm font-medium text-gray-900">{mode === 'MANAGED' ? 'Managed (Cobo MPC)' : 'Self-Custody'}</dd>
                                    </div>
                                    <div>
                                        <dt className="text-sm text-gray-500">Asset Name</dt>
                                        <dd className="mt-1 text-sm font-medium text-gray-900">{formData.name}</dd>
                                    </div>
                                    <div>
                                        <dt className="text-sm text-gray-500">Ticker Symbol</dt>
                                        <dd className="mt-1 text-sm font-medium text-gray-900">{formData.symbol}</dd>
                                    </div>
                                    <div>
                                        <dt className="text-sm text-gray-500">Capital Structure</dt>
                                        <dd className="mt-1 text-sm font-medium text-gray-900">
                                            {formData.partitions.filter(p => p).map((p, i) => (
                                                <span key={i} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2">
                                                    {p}
                                                </span>
                                            ))}
                                        </dd>
                                    </div>
                                </dl>
                            </div>

                            <div className="flex items-start gap-3 p-4 bg-yellow-50 text-yellow-800 rounded-lg text-sm">
                                <ShieldCheck className="w-5 h-5 flex-shrink-0 mt-0.5" />
                                <p>
                                    By proceeding, you are deploying an ERC1400 security token contract to the blockchain.
                                    This action is irreversible and will incur gas fees.
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Actions */}
                    <div className="mt-8 pt-6 border-t border-gray-100 flex justify-between">
                        <button
                            onClick={() => step > 1 ? setStep(s => s - 1) : onComplete()}
                            className="btn-secondary"
                        >
                            {step > 1 ? 'Back' : 'Cancel'}
                        </button>

                        {step < 3 ? (
                            <button
                                onClick={() => setStep(s => s + 1)}
                                disabled={!formData.name || !formData.symbol}
                                className="btn-primary"
                            >
                                Continue <ChevronRight className="w-4 h-4 ml-2" />
                            </button>
                        ) : (
                            <button
                                onClick={handleDeploy}
                                disabled={loading}
                                className="btn-primary bg-green-600 hover:bg-green-700 focus:ring-green-500"
                            >
                                {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Check className="w-4 h-4 mr-2" />}
                                Confirm Deployment
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
