import React, { useState, useEffect } from 'react';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || '/api';

// Helper function to format wei to token amount (divide by 10^18)
const formatTokenAmount = (weiAmount) => {
    if (!weiAmount || weiAmount === '0') return '0';
    const tokens = BigInt(weiAmount) / BigInt(10 ** 18);
    return tokens.toLocaleString();
};

export default function IssuerPanel({ contractAddress, setContractAddress, walletId, setWalletId, chainId, setChainId }) {
    const [rewardTokenAddress, setRewardTokenAddress] = useState('');
    const [depositAmount, setDepositAmount] = useState('');
    const [rewardsInfo, setRewardsInfo] = useState(null);
    const [loadingSetToken, setLoadingSetToken] = useState(false);
    const [loadingSnapshot, setLoadingSnapshot] = useState(false);
    const [loadingDeposit, setLoadingDeposit] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    // Fetch rewards info when contract address changes
    useEffect(() => {
        if (contractAddress && contractAddress.startsWith('0x')) {
            fetchRewardsInfo();
        }
    }, [contractAddress, chainId]);

    const fetchRewardsInfo = async () => {
        try {
            const response = await fetch(`${API_URL}/rewards/info/${contractAddress}?chain_id=${chainId}`);
            const data = await response.json();
            if (data.status === 'success') {
                setRewardsInfo(data.data);
            }
        } catch (err) {
            console.error('Failed to fetch rewards info:', err);
        }
    };

    const handleSetRewardToken = async () => {
        if (!contractAddress || !rewardTokenAddress || !walletId) {
            setError('Please fill in all fields');
            return;
        }

        setLoadingSetToken(true);
        setError(null);
        setSuccess(null);

        try {
            const response = await fetch(`${API_URL}/rewards/set-reward-token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contract_address: contractAddress,
                    reward_token_address: rewardTokenAddress,
                    wallet_id: walletId,
                    chain_id: chainId
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                setSuccess(`Reward token set! TX ID: ${data.tx_id}`);
                setTimeout(() => fetchRewardsInfo(), 3000);
            } else {
                setError(data.detail || 'Failed to set reward token');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoadingSetToken(false);
        }
    };

    const handleTakeSnapshot = async () => {
        if (!contractAddress || !walletId) {
            setError('Please enter contract address and wallet ID');
            return;
        }

        setLoadingSnapshot(true);
        setError(null);
        setSuccess(null);

        try {
            const response = await fetch(`${API_URL}/rewards/take-snapshot`, {
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
                setSuccess(`Snapshot taken! TX ID: ${data.tx_id}`);
                setTimeout(() => fetchRewardsInfo(), 3000);
            } else {
                setError(data.detail || 'Failed to take snapshot');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoadingSnapshot(false);
        }
    };

    const handleDepositRewards = async () => {
        if (!contractAddress || !depositAmount || !walletId) {
            setError('Please fill in all fields');
            return;
        }

        setLoadingDeposit(true);
        setError(null);
        setSuccess(null);

        try {
            // Convert token amount to wei (multiply by 10^18)
            // Send as string because JavaScript parseInt cannot handle numbers > 2^53
            const weiAmount = (BigInt(depositAmount) * BigInt(10 ** 18)).toString();

            const response = await fetch(`${API_URL}/rewards/deposit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contract_address: contractAddress,
                    amount: weiAmount,  // Send as string, Pydantic will parse as int
                    wallet_id: walletId,
                    chain_id: chainId,
                    auto_approve: true
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                const result = data.data;
                let message = '';
                if (result.approve_tx_id) {
                    message += `Approval TX: ${result.approve_tx_id}\n`;
                }
                message += `Deposit TX: ${result.deposit_tx_id}`;
                setSuccess(message);
                setTimeout(() => fetchRewardsInfo(), 5000);
            } else {
                setError(data.detail || 'Failed to deposit rewards');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoadingDeposit(false);
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
                            placeholder="0x..."
                            className="input-field font-mono text-sm"
                        />
                    </div>

                    <div>
                        <label className="label">Issuer Wallet ID (Cobo)</label>
                        <input
                            type="text"
                            value={walletId}
                            onChange={(e) => setWalletId(e.target.value)}
                            placeholder="Your Cobo Wallet ID"
                            className="input-field"
                        />
                    </div>
                </div>
            </div>

            {/* Current Status */}
            {rewardsInfo && (
                <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
                    <h3 className="text-sm font-semibold text-slate-900 uppercase tracking-wider mb-4">Current Status</h3>
                    <dl className="grid grid-cols-2 gap-x-4 gap-y-4 text-sm">
                        <div>
                            <dt className="text-slate-500">Reward Token</dt>
                            <dd className="mt-1 text-slate-900 font-mono text-xs break-all">
                                {rewardsInfo.rewardToken === '0x0000000000000000000000000000000000000000'
                                    ? 'Not Set'
                                    : `${rewardsInfo.rewardToken.slice(0, 6)}...${rewardsInfo.rewardToken.slice(-4)}`}
                            </dd>
                        </div>
                        <div>
                            <dt className="text-slate-500">Snapshot Block</dt>
                            <dd className="mt-1 text-slate-900">{rewardsInfo.snapshotBlock || 'Not Taken'}</dd>
                        </div>
                        <div>
                            <dt className="text-slate-500">Total Snapshot Supply</dt>
                            <dd className="mt-1 text-slate-900">{formatTokenAmount(rewardsInfo.totalSnapshotSupply)}</dd>
                        </div>
                        <div>
                            <dt className="text-slate-500">Total Reward Amount</dt>
                            <dd className="mt-1 text-slate-900">{formatTokenAmount(rewardsInfo.totalRewardAmount)}</dd>
                        </div>
                        <div className="col-span-2">
                            <dt className="text-slate-500">Current Block</dt>
                            <dd className="mt-1 text-slate-900">{rewardsInfo.currentBlock}</dd>
                        </div>
                    </dl>
                </div>
            )}

            {/* Step 1: Set Reward Token */}
            <div className="space-y-4">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                        1
                    </div>
                    <h3 className="text-lg font-medium text-slate-900">Set Reward Token</h3>
                </div>
                <div className="ml-11 space-y-4">
                    <div>
                        <label className="label">Reward Token Address (ERC20)</label>
                        <input
                            type="text"
                            value={rewardTokenAddress}
                            onChange={(e) => setRewardTokenAddress(e.target.value)}
                            placeholder="0x..."
                            className="input-field font-mono text-sm"
                        />
                    </div>
                    <button
                        onClick={handleSetRewardToken}
                        disabled={loadingSetToken}
                        className="btn-primary"
                    >
                        {loadingSetToken ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                        Set Reward Token
                    </button>
                </div>
            </div>

            {/* Step 2: Take Snapshot */}
            <div className="space-y-4">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                        2
                    </div>
                    <h3 className="text-lg font-medium text-slate-900">Take Snapshot</h3>
                </div>
                <div className="ml-11 space-y-4">
                    <p className="text-sm text-slate-600">
                        Takes a snapshot 20 blocks before the current block to determine token holder balances.
                    </p>
                    <button
                        onClick={handleTakeSnapshot}
                        disabled={loadingSnapshot}
                        className="btn-primary"
                    >
                        {loadingSnapshot ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                        Take Snapshot
                    </button>
                </div>
            </div>

            {/* Step 3: Deposit Rewards */}
            <div className="space-y-4">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-emerald-600 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                        3
                    </div>
                    <h3 className="text-lg font-medium text-slate-900">Deposit Rewards</h3>
                </div>
                <div className="ml-11 space-y-4">
                    <div>
                        <label className="label">Amount (in tokens)</label>
                        <input
                            type="number"
                            value={depositAmount}
                            onChange={(e) => setDepositAmount(e.target.value)}
                            placeholder="100"
                            className="input-field font-mono text-sm"
                        />
                        <p className="text-xs text-slate-500 mt-1">
                            Enter token amount. Will be converted to wei automatically. Auto-approval enabled.
                        </p>
                    </div>
                    <button
                        onClick={handleDepositRewards}
                        disabled={loadingDeposit}
                        className="btn-primary bg-emerald-600 hover:bg-emerald-700 focus:ring-emerald-500"
                    >
                        {loadingDeposit ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                        Deposit Rewards
                    </button>
                </div>
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
                    <p className="text-sm whitespace-pre-line">{success}</p>
                </div>
            )}
        </div>
    );
}
