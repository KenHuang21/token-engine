export default function ErrorDisplay({ error, onDismiss }) {
    if (!error) return null;

    return (
        <div className="bg-red-50 border border-red-300 rounded p-4 mb-4">
            <div className="flex justify-between items-start">
                <div>
                    <h3 className="font-semibold text-red-800">Deployment Failed</h3>
                    <p className="text-red-700 mt-1 text-sm">
                        {error.message || 'An unknown error occurred. Please try again.'}
                    </p>
                    {error.detail && (
                        <p className="text-red-600 mt-2 text-xs font-mono bg-red-100 p-2 rounded">
                            {error.detail}
                        </p>
                    )}
                </div>
                <button
                    onClick={onDismiss}
                    className="text-red-800 hover:text-red-900 text-xl font-bold leading-none"
                    aria-label="Dismiss error"
                >
                    ×
                </button>
            </div>
        </div>
    );
}
