import { useState, useEffect } from 'react';
import { ArenaApiClient } from './api/client';
import { BattleFlow } from './components/BattleFlow';
import './styles/components.css';

function App() {
  // Use environment variable for API base URL, fallback to localhost for dev
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';
  const [apiClient] = useState(() => new ArenaApiClient(apiBaseUrl));
  const [isConnected, setIsConnected] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    setIsChecking(true);
    setError(null);

    try {
      const health = await apiClient.health();
      console.log('Backend health:', health);
      setIsConnected(true);
    } catch (err) {
      console.error('Connection check failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to connect to backend');
      setIsConnected(false);
    } finally {
      setIsChecking(false);
    }
  };

  if (isChecking) {
    return (
      <div className="app">
        <div className="connection-screen">
          <h1>PCG Arena</h1>
          <p>Connecting to backend...</p>
        </div>
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="app">
        <div className="connection-screen error">
          <h1>PCG Arena</h1>
          <p className="error-message">{error}</p>
          <button onClick={checkConnection}>Retry Connection</button>
          <p className="hint">
            Make sure the backend is running at {apiBaseUrl}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>PCG Arena</h1>
        <p className="subtitle">Mario Level Rating Platform</p>
      </header>
      <main className="app-main">
        <BattleFlow apiClient={apiClient} />
      </main>
    </div>
  );
}

export default App;

