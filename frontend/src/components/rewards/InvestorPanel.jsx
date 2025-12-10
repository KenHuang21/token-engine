import React, { useState, useEffect } from 'react';
import { Loader2, CheckCircle2, AlertCircle, TrendingUp, Wallet } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || '/api';

// Web3 import for browser wallet integration
let ethers;
if (typeof window !== 'undefined') {
    import('https://cdn.jsdelivr.net/npm/ethers@5.7.2/dist/ethers.esm.min.js')
        .then(module => { ethers = module; })
        .catch(err => console.error('Failed to load ethers', err));
}

export default function InvestorPanel({ contractAddress, setContractAddress, walletId, setWalletId, chainId, setChainId }) {
    const [investorAddress, setInvestorAddress] = useState('');
    const [claimableData, setClaimableData] = useState(null);
    const [loadingClaimable, setLoadingClaimable] = useState(false);
    const [loadingClaim, setLoadingClaim] = useState(false);
    const [loadingDelegate, setLoadingDelegate] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [delegateeAddress, setDelegateeAddress] = useState('');

    // Auto-fetch wallet ID when investor address changes
    useEffect(() => {
        const fetchWalletId = async () => {
            if (!investorAddress || investorAddress.length < 10) return;

            try {
                const response = await fetch(
                    `${API_URL}/wallets/find-by-address/${investorAddress}?chain_id=${chainId}`
                );
                const data = await response.json();

                if (data.status === 'success') {
                    setWalletId(data.wallet_id);
                    console.log(`Auto-selected wallet ID: ${data.wallet_id} for ${data.wallet_name}`);
                } else if (data.status === 'not_found') {
                    // Use default wallet ID if address not found in Cobo
                    setWalletId(data.wallet_id);
                    console.log(data.message);
                }
            } catch (err) {
                console.error('Error fetching wallet ID:', err);
                // Silently fail, keep current wallet ID
            }
        };

        fetchWalletId();
    }, [investorAddress, chainId, setWalletId]);

    const fetchClaimable = async () => {
        if (!contractAddress || !investorAddress) {
            setError('Please enter contract address and investor address');
            return;
        }

        setLoadingClaimable(true);
        setError(null);

        try {
            const response = await fetch(
                `${API_URL}/rewards/claimable/${contractAddress}/${investorAddress}?chain_id=${chainId}`
            );
            const data = await response.json();

            if (data.status === 'success') {
                setClaimableData(data.data);
            } else {
                setError(data.detail || 'Failed to fetch claimable amount');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoadingClaimable(false);
        }
    };

    const handleClaim = async () => {
        if (!contractAddress || !walletId) {
            setError('Please enter contract address and wallet ID');
            return;
        }

        setLoadingClaim(true);
        setError(null);
        setSuccess(null);

        try {
            const response = await fetch(`${API_URL}/rewards/claim`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contract_address: contractAddress,
                    wallet_id: walletId,
                    chain_id: chainId
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                setSuccess(`Claim transaction submitted! TX ID: ${data.tx_id}`);
                setTimeout(() => fetchClaimable(), 5000);
            } else {
                setError(data.detail || 'Failed to claim rewards');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoadingClaim(false);
        }
    };

    const handleDelegate = async () => {
        if (!contractAddress || !walletId) {
            setError('Please enter token contract address and wallet ID');
            return;
        }

        const targetDelegatee = delegateeAddress || investorAddress;
        if (!targetDelegatee) {
            setError('Please enter investor address or specify delegatee');
            return;
        }

        setLoadingDelegate(true);
        setError(null);
        setSuccess(null);

        try {
            const response = await fetch(`${API_URL}/rewards/delegate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    token_contract_address: contractAddress,
                    delegatee_address: targetDelegatee,
                    wallet_id: walletId,
                    chain_id: chainId
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                setSuccess(`Delegation successful! TX ID: ${data.tx_id}. Your tokens now have voting power for snapshots.`);
            } else {
                setError(data.detail || 'Failed to delegate tokens');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoadingDelegate(false);
        }
    };

    const handleDelegateWithWallet = async () => {
        if (!contractAddress) {
            setError('Please enter token contract address');
            return;
        }

        setLoadingDelegate(true);
        setError(null);
        setSuccess(null);

        try {
            // Check if ethers is loaded
            if (!ethers) {
                throw new Error('Ethers library not loaded yet. Please refresh and try again.');
            }

            // Check if MetaMask is installed
            if (typeof window.ethereum === 'undefined') {
                throw new Error('MetaMask is not installed. Please install MetaMask to continue.');
            }

            // Request account access
            await window.ethereum.request({ method: 'eth_requestAccounts' });

            const provider = new ethers.providers.Web3Provider(window.ethereum);
            const signer = provider.getSigner();
            const signerAddress = await signer.getAddress();

            console.log('Connected wallet:', signerAddress);

            // Delegate to self by default, or to specified delegatee
            const targetDelegatee = delegateeAddress || signerAddress;

            // ERC20Votes delegate ABI
            const delegateABI = [
                "function delegate(address delegatee) external"
            ];

            const contract = new ethers.Contract(contractAddress, delegateABI, signer);

            // Send delegation transaction
            const tx = await contract.delegate(targetDelegatee);

            setSuccess(`Delegation transaction sent! TX: ${tx.hash}. Waiting for confirmation...`);

            // Wait for confirmation
            const receipt = await tx.wait();

            setSuccess(`✅ Delegation confirmed! TX: ${receipt.transactionHash}. Your tokens now have voting power. Take a new snapshot!`);

        } catch (err) {
            console.error('Delegation error:', err);
            if (err.code === 4001) {
                setError('Transaction rejected by user');
            } else if (err.code === -32002) {
                setError('MetaMask is already processing a request. Please check MetaMask.');
            } else {
                setError(err.message || 'Failed to delegate tokens');
            }
        } finally {
            setLoadingDelegate(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Contract Configuration */}
            <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
                <h3 className="text-sm font-semibold text-slate-900 uppercase tracking-wider mb-4">Contract Configuration</h3>

                <div className="space-y-4">
                    <div>
                        <label className="label">Chain ID</label>
                        <select
                            value={chainId}
                            onChange={(e) => setChainId(e.target.value)}
                            className="input-field"
                        >
                            <option value="ETH_SEPOLIA">Sepolia Testnet</option>
                            <option value="ETH">Ethereum Mainnet</option>
                            <option value="MATIC_POLYGON">Polygon</option>
                            <option value="BSC_BNB">BSC</option>
                        </select>
                    </div>

                    <div>
                        <label className="label">Rewards Contract Address</label>
                        <input
                            type="text"
                            value={contractAddress}
                            onChange={(e) => setContractAddress(e.target.value)}
                            placeholder="0x144d8a909e3a7752c0d86d2972ecc73ae1f68836"
                            className="input-field font-mono text-sm"
                        />
                    </div>

                    <div>
                        <label className="label">Investor Wallet ID (Cobo)</label>
                        <input
                            type="text"
                            value={walletId}
                            onChange={(e) => setWalletId(e.target.value)}
                            placeholder="Your Cobo Wallet ID for claiming"
                            className="input-field"
                        />
                    </div>
                </div>
            </div>

            {/* Delegate Tokens */}
            <div className="bg-blue-50 rounded-xl p-6 border border-blue-200">
                <h3 className="text-lg font-medium text-slate-900 mb-2">Delegate Tokens (Required for Rewards)</h3>
                <p className="text-sm text-slate-600 mb-4">
                    ⚠️ ERC20Votes tokens must be delegated for voting power. Delegate to yourself to enable snapshot eligibility.
                </p>

                <div className="space-y-4">
                    <div>
                        <label className="label">Token Contract Address</label>
                        <p className="text-xs text-slate-500 mb-2">Usually same as rewards contract address</p>
                        <input
                            type="text"
                            value={contractAddress}
                            readOnly
                            className="input-field font-mono text-sm bg-slate-100"
                        />
                    </div>

                    <div>
                        <label className="label">Delegatee Address (leave empty to delegate to yourself)</label>
                        <input
                            type="text"
                            value={delegateeAddress}
                            onChange={(e) => setDelegateeAddress(e.target.value)}
                            placeholder={investorAddress || "Will use investor address if empty"}
                            className="input-field font-mono text-sm"
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <button
                            onClick={handleDelegate}
                            disabled={loadingDelegate}
                            className="btn-primary bg-blue-600 hover:bg-blue-700 focus:ring-blue-500"
                        >
                            {loadingDelegate ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                            Delegate via Cobo
                        </button>

                        <button
                            onClick={handleDelegateWithWallet}
                            disabled={loadingDelegate}
                            className="btn-primary bg-orange-600 hover:bg-orange-700 focus:ring-orange-500"
                        >
                            {loadingDelegate ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Wallet className="w-4 h-4 mr-2" />}
                            Delegate with MetaMask
                        </button>
                    </div>

                    <div className="bg-blue-100 border border-blue-300 rounded-lg px-4 py-3 text-sm text-blue-800">
                        <p className="font-semibold mb-1">Which option to use?</p>
                        <ul className="list-disc list-inside space-y-1 text-xs">
                            <li><strong>Cobo:</strong> Use if wallet is managed by Cobo (requires Wallet ID)</li>
                            <li><strong>MetaMask:</strong> Use if you control the private key (connects your browser wallet)</li>
                        </ul>
                    </div>

                    <p className="text-xs text-slate-500">
                        💡 After delegation, take a new snapshot for your tokens to count in rewards
                    </p>
                </div>
            </div>

            {/* Check Claimable Amount */}
            <div className="space-y-4">
                <h3 className="text-lg font-medium text-slate-900">Check Claimable Rewards</h3>

                <div className="space-y-4">
                    <div>
                        <label className="label">Investor Address</label>
                        <input
                            type="text"
                            value={investorAddress}
                            onChange={(e) => setInvestorAddress(e.target.value)}
                            placeholder="0x..."
                            className="input-field font-mono text-sm"
                        />
                        <p className="text-xs text-slate-500 mt-1">
                            The address that holds the tokens (can be queried without wallet ID)
                        </p>
                    </div>

                    <button
                        onClick={fetchClaimable}
                        disabled={loadingClaimable}
                        className="btn-secondary w-full sm:w-auto"
                    >
                        {loadingClaimable ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                        Check Claimable Amount
                    </button>
                </div>

                {/* Claimable Display */}
                {claimableData && (
                    <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
                        <div className="grid grid-cols-2 gap-6">
                            <div>
                                <p className="text-sm text-slate-500 mb-2">Claimable Amount</p>
                                <p className="text-3xl font-bold text-emerald-600">
                                    {(parseFloat(claimableData.claimable) / 1e18).toLocaleString()}
                                </p>
                                <p className="text-xs text-slate-500 mt-1">tokens</p>
                            </div>
                            <div>
                                <p className="text-sm text-slate-500 mb-2">Already Claimed</p>
                                <p className="text-2xl font-semibold text-slate-700">
                                    {(parseFloat(claimableData.claimed) / 1e18).toLocaleString()}
                                </p>
                                <p className="text-xs text-slate-500 mt-1">tokens</p>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Claim Rewards */}
            <div className="space-y-4">
                <h3 className="text-lg font-medium text-slate-900">Claim Your Rewards</h3>

                <p className="text-sm text-slate-600">
                    Click below to claim your available rewards. Make sure your wallet ID is entered above.
                </p>

                {claimableData && claimableData.claimable === '0' && (
                    <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 flex items-start gap-2">
                        <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                        <p className="text-sm text-amber-800">
                            No claimable rewards available for this address
                        </p>
                    </div>
                )}

                <button
                    onClick={handleClaim}
                    disabled={loadingClaim || (claimableData && claimableData.claimable === '0')}
                    className="btn-primary bg-emerald-600 hover:bg-emerald-700 focus:ring-emerald-500"
                >
                    {loadingClaim ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <TrendingUp className="w-4 h-4 mr-2" />}
                    Claim Rewards
                </button>

                <p className="text-xs text-slate-500">
                    💡 Tip: Rewards are distributed based on your token balance at the snapshot block
                </p>
            </div>

            {/* Messages */}
            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2">
                    <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <p className="text-sm">{error}</p>
                </div>
            )}

            {success && (
                <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-lg flex items-start gap-2">
                    <CheckCircle2 className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <p className="text-sm">{success}</p>
                </div>
            )}
        </div>
    );
}
