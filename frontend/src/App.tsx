import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { ArenaApiClient } from './api/client';
import { BattleFlow } from './components/BattleFlow';
import { BuilderPage } from './pages/BuilderPage';
import { AuthProvider } from './contexts/AuthContext';
import './styles/components.css';

// Navigation component
function Navigation() {
  const location = useLocation();
  
  return (
    <nav className="app-nav">
      <Link 
        to="/" 
        className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
      >
        Play
      </Link>
      <Link 
        to="/builder" 
        className={`nav-link ${location.pathname === '/builder' ? 'active' : ''}`}
      >
        Builder Profile
      </Link>
    </nav>
  );
}

function AppContent() {
  // In development, use empty string to go through Vite's proxy
  // In production, use the configured API base URL
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '';
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
        <Navigation />
      </header>
      <main className="app-main">
        <Routes>
          <Route path="/" element={<BattleFlow apiClient={apiClient} />} />
          <Route path="/builder" element={<BuilderPage />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
