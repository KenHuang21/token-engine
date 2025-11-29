export const getBlockExplorerUrl = (chain, address) => {
    if (!address) return '#';
    switch (chain) {
        case 'ETH':
            return `https://etherscan.io/address/${address}`;
        case 'SEPOLIA':
            return `https://sepolia.etherscan.io/address/${address}`;
        case 'BSC_BNB':
            return `https://bscscan.com/address/${address}`;
        case 'MATIC_POLYGON':
        case 'MATIC':
            return `https://polygonscan.com/address/${address}`;
        default:
            return '#';
    }
};
