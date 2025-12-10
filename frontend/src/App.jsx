import { useState } from 'react'
import DashboardLayout from './components/DashboardLayout';
import Dashboard from './components/Dashboard';
import DeployWizard from './components/DeployWizard';
import TokenManager from './components/TokenManager';
import RewardsDistribution from './pages/RewardsDistribution';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedToken, setSelectedToken] = useState(null);

  const handleTokenSelect = (token) => {
    setSelectedToken(token);
    setActiveTab('token_manager');
  };

  const renderContent = () => {
    if (activeTab === 'token_manager' && selectedToken) {
      return <TokenManager token={selectedToken} onBack={() => setActiveTab('dashboard')} />;
    }

    switch (activeTab) {
      case 'dashboard':
        return <Dashboard onSelectToken={handleTokenSelect} onDeploy={() => setActiveTab('deploy')} />;
      case 'deploy':
        return <DeployWizard onComplete={() => setActiveTab('dashboard')} />;
      case 'rewards':
        return <RewardsDistribution />;
      default:
        return <Dashboard onSelectToken={handleTokenSelect} />;
    }
  };

  return (
    <DashboardLayout activeTab={activeTab} setActiveTab={setActiveTab}>
      {renderContent()}
    </DashboardLayout>
  )
}

export default App
