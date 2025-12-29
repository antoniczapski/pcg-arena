import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth, GOOGLE_CLIENT_ID } from '../contexts/AuthContext';
import '../styles/builder.css';

// In development, use relative paths to go through Vite's proxy
// In production, use the configured API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

interface GeneratorInfo {
  generator_id: string;
  name: string;
  version: string;
  description: string;
  tags: string[];
  documentation_url: string | null;
  is_active: boolean;
  level_count: number;
  rating: number;
  games_played: number;
  wins: number;
  losses: number;
  ties: number;
  created_at_utc: string;
  updated_at_utc: string;
}

interface GeneratorsResponse {
  protocol_version: string;
  user_id: string;
  max_generators: number;
  min_levels_required: number;
  max_levels_allowed: number;
  generators: GeneratorInfo[];
}

export function BuilderPage() {
  const { user, isAuthenticated, isLoading: authLoading, logout, isGoogleReady, renderGoogleButton, loginWithEmail, registerWithEmail, resendVerificationEmail } = useAuth();
  const [generators, setGenerators] = useState<GeneratorInfo[]>([]);
  const [maxGenerators, setMaxGenerators] = useState(3);
  const [minLevels, setMinLevels] = useState(50);
  const [maxLevels, setMaxLevels] = useState(200);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingGenerator, setEditingGenerator] = useState<string | null>(null);
  
  // Login/Register form state
  const [authMode, setAuthMode] = useState<'login' | 'register' | 'forgot'>('login');
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authDisplayName, setAuthDisplayName] = useState('');
  const [authError, setAuthError] = useState<string | null>(null);
  const [authSubmitting, setAuthSubmitting] = useState(false);
  const [forgotPasswordSent, setForgotPasswordSent] = useState(false);
  
  // Google Sign-In button container ref (must be called before any early returns)
  const googleButtonRef = useRef<HTMLDivElement>(null);

  const fetchGenerators = useCallback(async () => {
    if (!isAuthenticated) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/v1/builders/me/generators`, {
        credentials: 'include',
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error?.message || 'Failed to fetch generators');
      }

      const data: GeneratorsResponse = await response.json();
      setGenerators(data.generators);
      setMaxGenerators(data.max_generators);
      setMinLevels(data.min_levels_required);
      setMaxLevels(data.max_levels_allowed);
    } catch (err) {
      console.error('Failed to fetch generators:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch generators');
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    fetchGenerators();
  }, [fetchGenerators]);

  // Render Google button when ready
  // Re-render after auth errors or mode changes to ensure button is visible
  useEffect(() => {
    if (googleButtonRef.current && isGoogleReady && !isAuthenticated) {
      // Clear any existing content first
      googleButtonRef.current.innerHTML = '';
      renderGoogleButton(googleButtonRef.current);
    }
  }, [isGoogleReady, isAuthenticated, renderGoogleButton, authMode, authError]);

  const handleDelete = async (generatorId: string) => {
    if (!confirm(`Are you sure you want to delete "${generatorId}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/v1/builders/generators/${generatorId}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error?.message || 'Failed to delete generator');
      }

      await fetchGenerators();
    } catch (err) {
      console.error('Failed to delete generator:', err);
      alert(err instanceof Error ? err.message : 'Failed to delete generator');
    }
  };

  if (authLoading) {
    return (
      <div className="builder-page">
        <div className="builder-loading">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Handle email login/register form submission
  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    setAuthSubmitting(true);
    
    try {
      if (authMode === 'login') {
        await loginWithEmail(authEmail, authPassword);
      } else if (authMode === 'register') {
        if (!authDisplayName.trim()) {
          throw new Error('Display name is required');
        }
        await registerWithEmail(authEmail, authPassword, authDisplayName);
      }
      // Note: 'forgot' mode has its own form handler
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setAuthSubmitting(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="builder-page">
        <div className="builder-login">
          <h2>Builder Profile</h2>
          <p>Sign in to submit your own generators and compete on the leaderboard.</p>
          
          {/* Google Sign-In Button */}
          {GOOGLE_CLIENT_ID && (
            <div className="google-login-container">
              <div ref={googleButtonRef} className="google-button-wrapper"></div>
              {!isGoogleReady && <p className="login-hint">Loading Google Sign-In...</p>}
            </div>
          )}
          
          <div className="login-divider">
            <span>or</span>
          </div>
          
          {/* Email/Password Login Form */}
          {authMode !== 'forgot' ? (
            <>
              <div className="auth-tabs">
                <button 
                  className={`auth-tab ${authMode === 'login' ? 'active' : ''}`}
                  onClick={() => { setAuthMode('login'); setAuthError(null); }}
                >
                  Sign In
                </button>
                <button 
                  className={`auth-tab ${authMode === 'register' ? 'active' : ''}`}
                  onClick={() => { setAuthMode('register'); setAuthError(null); }}
                >
                  Create Account
                </button>
              </div>
              
              <form className="auth-form" onSubmit={handleAuthSubmit}>
                {authError && <div className="auth-error">{authError}</div>}
                
                <div className="form-group">
                  <label htmlFor="auth-email">Email</label>
                  <input
                    id="auth-email"
                    type="email"
                    value={authEmail}
                    onChange={(e) => setAuthEmail(e.target.value)}
                    placeholder="your@email.com"
                    required
                    disabled={authSubmitting}
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="auth-password">Password</label>
                  <input
                    id="auth-password"
                    type="password"
                    value={authPassword}
                    onChange={(e) => setAuthPassword(e.target.value)}
                    placeholder={authMode === 'register' ? 'At least 8 characters' : 'Your password'}
                    required
                    minLength={authMode === 'register' ? 8 : undefined}
                    disabled={authSubmitting}
                  />
                </div>
                
                {authMode === 'register' && (
                  <div className="form-group">
                    <label htmlFor="auth-display-name">Display Name</label>
                    <input
                      id="auth-display-name"
                      type="text"
                      value={authDisplayName}
                      onChange={(e) => setAuthDisplayName(e.target.value)}
                      placeholder="How you'll appear on the leaderboard"
                      required
                      disabled={authSubmitting}
                    />
                  </div>
                )}
                
                <button type="submit" className="login-button" disabled={authSubmitting}>
                  {authSubmitting ? 'Please wait...' : (authMode === 'login' ? 'Sign In' : 'Create Account')}
                </button>
              </form>
              
              {authMode === 'login' && (
                <button 
                  className="forgot-password-link"
                  onClick={() => { setAuthMode('forgot'); setAuthError(null); setForgotPasswordSent(false); }}
                >
                  Forgot your password?
                </button>
              )}
            </>
          ) : (
            /* Forgot Password Form */
            <div className="auth-form">
              <h3 style={{ textAlign: 'center', marginBottom: '1rem' }}>Reset Password</h3>
              
              {forgotPasswordSent ? (
                <div className="password-reset-success">
                  <p>If an account exists with that email, you'll receive a password reset link shortly.</p>
                  <p>Check your inbox (and spam folder).</p>
                </div>
              ) : (
                <>
                  {authError && <div className="auth-error">{authError}</div>}
                  <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem', textAlign: 'center' }}>
                    Enter your email and we'll send you a reset link.
                  </p>
                  <form onSubmit={async (e) => {
                    e.preventDefault();
                    setAuthSubmitting(true);
                    setAuthError(null);
                    try {
                      const response = await fetch(`${API_BASE_URL}/v1/auth/forgot-password`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email: authEmail }),
                      });
                      if (response.ok) {
                        setForgotPasswordSent(true);
                      } else {
                        const data = await response.json();
                        setAuthError(data.error?.message || 'Failed to send reset email');
                      }
                    } catch (err) {
                      setAuthError('An error occurred. Please try again.');
                    } finally {
                      setAuthSubmitting(false);
                    }
                  }}>
                    <div className="form-group">
                      <label htmlFor="forgot-email">Email</label>
                      <input
                        id="forgot-email"
                        type="email"
                        value={authEmail}
                        onChange={(e) => setAuthEmail(e.target.value)}
                        placeholder="your@email.com"
                        required
                        disabled={authSubmitting}
                      />
                    </div>
                    <button type="submit" className="login-button" disabled={authSubmitting}>
                      {authSubmitting ? 'Sending...' : 'Send Reset Link'}
                    </button>
                  </form>
                </>
              )}
              
              <button 
                className="forgot-password-link"
                onClick={() => { setAuthMode('login'); setAuthError(null); }}
                style={{ marginTop: '1rem' }}
              >
                ← Back to Sign In
              </button>
            </div>
          )}
          
          <p className="privacy-notice">
            By signing in, you agree to our use of your email and display name
            to identify your generator submissions.
          </p>
        </div>
      </div>
    );
  }

  // Show email verification required screen for unverified users
  if (user && !user.is_email_verified) {
    return (
      <div className="email-required-page">
        <div className="email-required-card">
          <div className="icon">📧</div>
          <h2>Email Verification Required</h2>
          <p>
            Before you can submit generators, please verify your email address.
          </p>
          <p>
            We sent a verification link to:<br />
            <span className="email-highlight">{user.email}</span>
          </p>
          <p>
            Check your inbox (and spam folder) for the verification email, then click the link to verify.
          </p>
          
          <div className="email-required-actions">
            <button 
              className="resend-button"
              onClick={resendVerificationEmail}
            >
              Resend Verification Email
            </button>
            <button className="logout-button" onClick={logout}>
              Sign Out
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="builder-page">
      <div className="builder-header">
        <div className="builder-user-info">
          <h2>Builder Profile</h2>
          <p>Welcome, <strong>{user?.display_name}</strong> ({user?.email})</p>
        </div>
        <button className="logout-button" onClick={logout}>
          Sign Out
        </button>
      </div>

      {error && (
        <div className="builder-error">
          <p>{error}</p>
          <button onClick={fetchGenerators}>Retry</button>
        </div>
      )}

      <div className="builder-stats">
        <div className="stat-card">
          <span className="stat-value">{generators.length}</span>
          <span className="stat-label">/ {maxGenerators} Generators</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{minLevels}-{maxLevels}</span>
          <span className="stat-label">Levels Required</span>
        </div>
      </div>

      <div className="builder-generators">
        <div className="generators-header">
          <h3>Your Generators</h3>
          {generators.length < maxGenerators && !showForm && (
            <button 
              className="add-generator-button"
              onClick={() => { setShowForm(true); setEditingGenerator(null); }}
            >
              + Add Generator
            </button>
          )}
        </div>

        {showForm && (
          <GeneratorForm
            editingId={editingGenerator}
            minLevels={minLevels}
            maxLevels={maxLevels}
            onSuccess={() => {
              setShowForm(false);
              setEditingGenerator(null);
              fetchGenerators();
            }}
            onCancel={() => {
              setShowForm(false);
              setEditingGenerator(null);
            }}
          />
        )}

        {isLoading ? (
          <div className="generators-loading">
            <p>Loading generators...</p>
          </div>
        ) : generators.length === 0 ? (
          <div className="generators-empty">
            <p>You haven't submitted any generators yet.</p>
            <p>Create your first generator to start competing on the leaderboard!</p>
          </div>
        ) : (
          <div className="generators-list">
            {generators.map((gen) => (
              <GeneratorCard
                key={gen.generator_id}
                generator={gen}
                onEdit={() => {
                  setEditingGenerator(gen.generator_id);
                  setShowForm(true);
                }}
                onDelete={() => handleDelete(gen.generator_id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface GeneratorCardProps {
  generator: GeneratorInfo;
  onEdit: () => void;
  onDelete: () => void;
}

function GeneratorCard({ generator, onEdit, onDelete }: GeneratorCardProps) {
  const winRate = generator.games_played > 0
    ? ((generator.wins / generator.games_played) * 100).toFixed(1)
    : '-';

  return (
    <div className="generator-card">
      <div className="generator-card-header">
        <div className="generator-info">
          <h4>{generator.name}</h4>
          <code className="generator-id">{generator.generator_id}</code>
        </div>
        <div className="generator-version">v{generator.version}</div>
      </div>

      <p className="generator-description">
        {generator.description || 'No description provided.'}
      </p>

      {generator.tags.length > 0 && (
        <div className="generator-tags">
          {generator.tags.map((tag) => (
            <span key={tag} className="tag">{tag}</span>
          ))}
        </div>
      )}

      <div className="generator-stats">
        <div className="stat">
          <span className="stat-value">{generator.rating.toFixed(1)}</span>
          <span className="stat-label">Rating</span>
        </div>
        <div className="stat">
          <span className="stat-value">{generator.games_played}</span>
          <span className="stat-label">Games</span>
        </div>
        <div className="stat">
          <span className="stat-value">{generator.wins}W / {generator.losses}L</span>
          <span className="stat-label">Win Rate: {winRate}%</span>
        </div>
        <div className="stat">
          <span className="stat-value">{generator.level_count}</span>
          <span className="stat-label">Levels</span>
        </div>
      </div>

      <div className="generator-actions">
        <Link 
          to={`/generator/${generator.generator_id}`} 
          className="view-button"
        >
          View Levels
        </Link>
        <button className="edit-button" onClick={onEdit}>
          Update Version
        </button>
        <button className="delete-button" onClick={onDelete}>
          Delete
        </button>
      </div>
    </div>
  );
}

interface GeneratorFormProps {
  editingId: string | null;
  minLevels: number;
  maxLevels: number;
  onSuccess: () => void;
  onCancel: () => void;
}

function GeneratorForm({ editingId, minLevels, maxLevels, onSuccess, onCancel }: GeneratorFormProps) {
  const [generatorId, setGeneratorId] = useState('');
  const [name, setName] = useState('');
  const [version, setVersion] = useState('1.0.0');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState('');
  const [documentationUrl, setDocumentationUrl] = useState('');
  const [zipFile, setZipFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEditing = !!editingId;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!zipFile) {
      setError('Please select a ZIP file containing your levels');
      return;
    }

    setIsSubmitting(true);

    try {
      const formData = new FormData();
      formData.append('generator_id', isEditing ? editingId : generatorId);
      formData.append('name', name);
      formData.append('version', version);
      formData.append('description', description);
      formData.append('tags', tags);
      formData.append('documentation_url', documentationUrl);
      formData.append('levels_zip', zipFile);

      const url = isEditing
        ? `${API_BASE_URL}/v1/builders/generators/${editingId}/upload`
        : `${API_BASE_URL}/v1/builders/generators/upload`;

      const response = await fetch(url, {
        method: isEditing ? 'PUT' : 'POST',
        credentials: 'include',
        body: formData,
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error?.message || 'Failed to submit generator');
      }

      onSuccess();
    } catch (err) {
      console.error('Failed to submit generator:', err);
      setError(err instanceof Error ? err.message : 'Failed to submit generator');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="generator-form" onSubmit={handleSubmit}>
      <h4>{isEditing ? `Update ${editingId}` : 'Create New Generator'}</h4>

      {error && <div className="form-error">{error}</div>}

      {!isEditing && (
        <div className="form-group">
          <label htmlFor="generator_id">Generator ID *</label>
          <input
            id="generator_id"
            type="text"
            value={generatorId}
            onChange={(e) => setGeneratorId(e.target.value)}
            placeholder="e.g., my-generator-v1"
            pattern="[a-zA-Z][a-zA-Z0-9_-]{2,31}"
            required
            disabled={isSubmitting}
          />
          <small>3-32 characters. Start with a letter. Only alphanumeric, hyphens, underscores.</small>
        </div>
      )}

      <div className="form-group">
        <label htmlFor="name">Display Name *</label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g., My Awesome Generator"
          minLength={3}
          maxLength={100}
          required
          disabled={isSubmitting}
        />
      </div>

      <div className="form-group">
        <label htmlFor="version">Version *</label>
        <input
          id="version"
          type="text"
          value={version}
          onChange={(e) => setVersion(e.target.value)}
          placeholder="e.g., 1.0.0"
          maxLength={20}
          required
          disabled={isSubmitting}
        />
      </div>

      <div className="form-group">
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe your generator..."
          maxLength={1000}
          rows={3}
          disabled={isSubmitting}
        />
      </div>

      <div className="form-group">
        <label htmlFor="tags">Tags (comma-separated)</label>
        <input
          id="tags"
          type="text"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          placeholder="e.g., evolutionary, grammar-based, neural"
          disabled={isSubmitting}
        />
        <small>Up to 10 tags.</small>
      </div>

      <div className="form-group">
        <label htmlFor="documentation_url">Documentation URL</label>
        <input
          id="documentation_url"
          type="url"
          value={documentationUrl}
          onChange={(e) => setDocumentationUrl(e.target.value)}
          placeholder="https://..."
          disabled={isSubmitting}
        />
      </div>

      <div className="form-group">
        <label htmlFor="levels_zip">Levels ZIP File *</label>
        <input
          id="levels_zip"
          type="file"
          accept=".zip"
          onChange={(e) => setZipFile(e.target.files?.[0] || null)}
          required
          disabled={isSubmitting}
        />
        <small>
          ZIP containing {minLevels}-{maxLevels} level files (.txt). 
          Each file must be 16 lines (variable width up to 250).
          See <a href="https://github.com/amidos2006/Mario-AI-Framework" target="_blank" rel="noopener noreferrer">level format docs</a>.
        </small>
      </div>

      <div className="form-actions">
        <button type="submit" className="submit-button" disabled={isSubmitting}>
          {isSubmitting ? 'Submitting...' : (isEditing ? 'Update Generator' : 'Create Generator')}
        </button>
        <button type="button" className="cancel-button" onClick={onCancel} disabled={isSubmitting}>
          Cancel
        </button>
      </div>
    </form>
  );
}

