import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { ArenaApiClient } from './api/client';
import { BattleFlow } from './components/BattleFlow';
import { BuilderPage } from './pages/BuilderPage';
import { GeneratorPage } from './pages/GeneratorPage';
import { LeaderboardPage } from './pages/LeaderboardPage';
import { VerifyEmailPage } from './pages/VerifyEmailPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';
import { AdminPage } from './pages/AdminPage';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import './styles/components.css';

// Navigation component
function Navigation() {
  const location = useLocation();
  const { user } = useAuth();
  const [isAdmin, setIsAdmin] = useState(false);
  
  // Check admin status
  useEffect(() => {
    const checkAdmin = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/v1/auth/me/admin`, {
          credentials: 'include',
        });
        const data = await response.json();
        setIsAdmin(data.is_admin);
      } catch {
        setIsAdmin(false);
      }
    };
    
    if (user) {
      checkAdmin();
    } else {
      setIsAdmin(false);
    }
  }, [user]);
  
  return (
    <nav className="app-nav">
      <Link 
        to="/" 
        className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
      >
        Play
      </Link>
      <Link 
        to="/leaderboard" 
        className={`nav-link ${location.pathname === '/leaderboard' ? 'active' : ''}`}
      >
        Leaderboard
      </Link>
      <Link 
        to="/builder" 
        className={`nav-link ${location.pathname === '/builder' ? 'active' : ''}`}
      >
        Builder Profile
      </Link>
      {isAdmin && (
        <Link 
          to="/admin" 
          className={`nav-link ${location.pathname === '/admin' ? 'active' : ''}`}
        >
          Admin
        </Link>
      )}
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
          <Route path="/leaderboard" element={<LeaderboardPage />} />
          <Route path="/builder" element={<BuilderPage />} />
          <Route path="/generator/:generatorId" element={<GeneratorPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/admin" element={<AdminPage />} />
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
