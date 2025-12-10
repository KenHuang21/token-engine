import React, { useState } from 'react';
import IssuerPanel from '../components/rewards/IssuerPanel';
import InvestorPanel from '../components/rewards/InvestorPanel';
import { Gift, Building2, UserCircle } from 'lucide-react';

export default function RewardsDistribution() {
  const [activeTab, setActiveTab] = useState('issuer');
  const [contractAddress, setContractAddress] = useState('0x47850e3ddb2effa666eb879ba9ceb2f99dfecb0b');
  const [walletId, setWalletId] = useState('896d80b5-e653-4941-a906-ea55f28503e1');
  const [chainId, setChainId] = useState('ETH_SEPOLIA');

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Rewards Distribution</h1>
        <p className="text-slate-500 mt-1">Configure and manage ERC20 token rewards for security token holders.</p>
      </div>

      {/* Info Banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex gap-3">
          <Gift className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-blue-800">
            <strong>How it works:</strong> Issuers set a reward token, take a snapshot of token holders, and deposit rewards.
            Investors can then claim their pro-rata share based on their holdings at the snapshot block.
          </p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="card">
        <div className="grid grid-cols-2 border-b border-slate-200">
          <button
            onClick={() => setActiveTab('issuer')}
            className={`py-4 px-6 flex items-center justify-center gap-2 font-medium transition-colors border-b-2 ${activeTab === 'issuer'
              ? 'border-indigo-600 text-indigo-700 bg-indigo-50/50'
              : 'border-transparent text-slate-600 hover:bg-slate-50'
              }`}
          >
            <Building2 className="w-4 h-4" />
            Issuer
          </button>
          <button
            onClick={() => setActiveTab('investor')}
            className={`py-4 px-6 flex items-center justify-center gap-2 font-medium transition-colors border-b-2 ${activeTab === 'investor'
              ? 'border-emerald-600 text-emerald-700 bg-emerald-50/50'
              : 'border-transparent text-slate-600 hover:bg-slate-50'
              }`}
          >
            <UserCircle className="w-4 h-4" />
            Investor
          </button>
        </div>

        <div className="p-8">
          {activeTab === 'issuer' ? (
            <IssuerPanel
              contractAddress={contractAddress}
              setContractAddress={setContractAddress}
              walletId={walletId}
              setWalletId={setWalletId}
              chainId={chainId}
              setChainId={setChainId}
            />
          ) : (
            <InvestorPanel
              contractAddress={contractAddress}
              setContractAddress={setContractAddress}
              walletId={walletId}
              setWalletId={setWalletId}
              chainId={chainId}
              setChainId={setChainId}
            />
          )}
        </div>
      </div>

      {/* Help Section */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Need Help?</h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-2">For Issuers:</h4>
            <ol className="list-decimal list-inside space-y-1 text-sm text-slate-600">
              <li>Set the ERC20 token to use as rewards</li>
              <li>Take a snapshot to record current token holder balances</li>
              <li>Deposit reward tokens (auto-approval enabled)</li>
            </ol>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-2">For Investors:</h4>
            <ol className="list-decimal list-inside space-y-1 text-sm text-slate-600">
              <li>Check your claimable rewards by entering your address</li>
              <li>Enter your Cobo Wallet ID to claim</li>
              <li>Click "Claim Rewards" to receive your tokens</li>
            </ol>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-slate-200">
          <p className="text-sm text-slate-500">
            <strong className="text-slate-700">Note:</strong> All transactions are processed through Cobo WaaS.
            Make sure your wallet has the appropriate roles (MANAGER_ROLE for issuers) and sufficient gas.
          </p>
        </div>
      </div>
    </div>
  );
}
