import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth, GOOGLE_CLIENT_ID } from '../contexts/AuthContext';

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

interface AdminStats {
  user: { email: string; is_admin: boolean };
  config: {
    matchmaking_policy: string;
    initial_rating: number;
    initial_rd: number;
    min_games_for_significance: number;
    target_battles_per_pair: number;
    rating_similarity_sigma: number;
    quality_bias_strength: number;
  };
  matchmaking: {
    total_generators: number;
    total_possible_pairs: number;
    pairs_with_battles: number;
    pairs_at_target: number;
    coverage_percent: number;
    target_coverage_percent: number;
    average_rd: number;
    new_generators_count: number;
  };
  generators: Array<{
    generator_id: string;
    name: string;
    rating: number;
    rd: number;
    games_played: number;
    wins: number;
    losses: number;
    ties: number;
    skips: number;
    needs_more_games: boolean;
  }>;
  coverage_gaps: {
    under_covered_pairs: Array<{ gen1: string; gen2: string; battles: number }>;
    missing_pairs: Array<{ gen1: string; gen2: string }>;
    total_missing: number;
  };
}

interface ConfusionMatrixData {
  generators: Array<{ id: string; name: string }>;
  matrix: Array<Array<{
    battles: number;
    wins: number;
    losses: number;
    ties: number;
    win_rate: number | null;
  } | null>>;
  coverage: {
    total_pairs: number;
    pairs_with_data: number;
    pairs_at_target: number;
    target_battles_per_pair: number;
    coverage_percent: number;
    target_coverage_percent: number;
  };
}

interface BuilderData {
  user_id: string;
  email: string;
  display_name: string;
  created_at: string;
  generator_count: number;
  generator_names: string[];
  best_rating: number;
}

interface GeneratorData {
  generator_id: string;
  name: string;
  is_active: boolean;
  created_at: string;
  owner_id: string | null;
  owner_email: string;
  owner_name: string;
  rating: number;
  games_played: number;
}

export function AdminPage() {
  const { user, isLoading: authLoading, isGoogleReady, renderGoogleButton } = useAuth();
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const [adminStats, setAdminStats] = useState<AdminStats | null>(null);
  const [confusionMatrix, setConfusionMatrix] = useState<ConfusionMatrixData | null>(null);
  const [builders, setBuilders] = useState<BuilderData[]>([]);
  const [allGenerators, setAllGenerators] = useState<GeneratorData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'matrix' | 'gaps' | 'export' | 'builders' | 'generators'>('overview');
  const [exportStatus, setExportStatus] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<{ type: 'builder' | 'generator'; id: string; name: string } | null>(null);
  const googleButtonRef = useRef<HTMLDivElement>(null);

  // Check admin status
  useEffect(() => {
    const checkAdmin = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/v1/auth/me/admin`, {
          credentials: 'include',
        });
        const data = await response.json();
        setIsAdmin(data.is_admin);
      } catch (err) {
        console.error('Failed to check admin status:', err);
        setIsAdmin(false);
      }
    };

    if (!authLoading) {
      checkAdmin();
    }
  }, [authLoading, user]);

  // Load admin stats when admin status is confirmed
  useEffect(() => {
    const loadData = async () => {
      if (!isAdmin) return;

      setIsLoading(true);
      setError(null);

      try {
        // Load admin stats
        const statsResponse = await fetch(`${API_BASE_URL}/v1/admin/stats`, {
          credentials: 'include',
        });
        
        if (!statsResponse.ok) {
          const errorData = await statsResponse.json();
          throw new Error(errorData.error?.message || 'Failed to load admin stats');
        }
        
        const statsData = await statsResponse.json();
        setAdminStats(statsData);

        // Load confusion matrix
        const matrixResponse = await fetch(`${API_BASE_URL}/v1/stats/confusion-matrix`);
        if (matrixResponse.ok) {
          const matrixData = await matrixResponse.json();
          setConfusionMatrix(matrixData);
        }

        // Load builders
        const buildersResponse = await fetch(`${API_BASE_URL}/v1/admin/builders`, {
          credentials: 'include',
        });
        if (buildersResponse.ok) {
          const buildersData = await buildersResponse.json();
          setBuilders(buildersData.builders);
        }

        // Load all generators
        const generatorsResponse = await fetch(`${API_BASE_URL}/v1/admin/generators`, {
          credentials: 'include',
        });
        if (generatorsResponse.ok) {
          const generatorsData = await generatorsResponse.json();
          setAllGenerators(generatorsData.generators);
        }
      } catch (err) {
        console.error('Failed to load admin data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setIsLoading(false);
      }
    };

    if (isAdmin === true) {
      loadData();
    } else if (isAdmin === false) {
      setIsLoading(false);
    }
  }, [isAdmin]);

  // Render Google button when ready and the user is not logged in
  useEffect(() => {
    // Only try to render when we know the user isn't logged in
    // and the container ref is available
    if (googleButtonRef.current && isGoogleReady && !user && !authLoading) {
      // Small delay to ensure DOM is ready
      const timer = setTimeout(() => {
        if (googleButtonRef.current) {
          renderGoogleButton(googleButtonRef.current);
        }
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [isGoogleReady, renderGoogleButton, user, authLoading]);

  // Loading state
  if (authLoading || isAdmin === null) {
    return (
      <div className="admin-page">
        <h2>Admin Dashboard</h2>
        <p>Checking access...</p>
      </div>
    );
  }

  // Not logged in
  if (!user) {
    return (
      <div className="admin-page">
        <h2>Admin Dashboard</h2>
        <div className="admin-login-required">
          <p>🔐 Admin access requires Google OAuth login.</p>
          <p style={{ marginBottom: '1rem', opacity: 0.7 }}>
            Only authorized admin emails can access this dashboard.
          </p>
          {GOOGLE_CLIENT_ID ? (
            <>
              <div ref={googleButtonRef} className="google-button-container" />
              <p style={{ marginTop: '1rem', fontSize: '0.85rem', opacity: 0.6 }}>
                Or <a href="/builder" style={{ color: 'var(--color-lime)' }}>go to Builder Profile</a> to sign in.
              </p>
            </>
          ) : (
            <p className="warning">Google OAuth not configured. Set VITE_GOOGLE_CLIENT_ID.</p>
          )}
        </div>
      </div>
    );
  }

  // Not admin
  if (!isAdmin) {
    return (
      <div className="admin-page">
        <h2>Admin Dashboard</h2>
        <div className="admin-access-denied">
          <p>⛔ Access Denied</p>
          <p>Your email ({user.email}) is not in the admin list.</p>
          <p style={{ marginTop: '1rem', opacity: 0.7 }}>
            Admin access requires OAuth login with an authorized email address.
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="admin-page">
        <h2>Admin Dashboard</h2>
        <div className="admin-error">
          <p>❌ Error: {error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  // Loading data
  if (isLoading || !adminStats) {
    return (
      <div className="admin-page">
        <h2>Admin Dashboard</h2>
        <p>Loading admin data...</p>
      </div>
    );
  }

  return (
    <div className="admin-page">
      <h2>Admin Dashboard</h2>
      <p className="admin-user">Logged in as: {adminStats.user.email} ✓</p>

      {/* Tabs */}
      <div className="admin-tabs">
        <button 
          className={activeTab === 'overview' ? 'active' : ''} 
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={activeTab === 'matrix' ? 'active' : ''} 
          onClick={() => setActiveTab('matrix')}
        >
          Confusion Matrix
        </button>
        <button 
          className={activeTab === 'gaps' ? 'active' : ''} 
          onClick={() => setActiveTab('gaps')}
        >
          Coverage Gaps
        </button>
        <button 
          className={activeTab === 'export' ? 'active' : ''} 
          onClick={() => setActiveTab('export')}
        >
          Data Export
        </button>
        <button 
          className={activeTab === 'builders' ? 'active' : ''} 
          onClick={() => setActiveTab('builders')}
        >
          Builders
        </button>
        <button 
          className={activeTab === 'generators' ? 'active' : ''} 
          onClick={() => setActiveTab('generators')}
        >
          Generators
        </button>
      </div>

      {/* Confirmation Modal */}
      {confirmDelete && (
        <div className="confirm-modal-overlay">
          <div className="confirm-modal">
            <h3>⚠️ Confirm Deletion</h3>
            <p>
              Are you sure you want to {confirmDelete.type === 'builder' ? 'ban' : 'delete'}{' '}
              <strong>{confirmDelete.name}</strong>?
            </p>
            {confirmDelete.type === 'builder' && (
              <p className="warning-text">
                This will remove the user account and all their generators. 
                Generators with battle history will be soft-deleted to preserve data.
              </p>
            )}
            {confirmDelete.type === 'generator' && (
              <p className="warning-text">
                This action cannot be undone. If this generator has battles, it will be marked inactive instead.
              </p>
            )}
            <div className="confirm-actions">
              <button className="cancel-btn" onClick={() => setConfirmDelete(null)}>
                Cancel
              </button>
              <button 
                className="danger-btn" 
                onClick={() => executeDelete(confirmDelete.type, confirmDelete.id)}
              >
                {confirmDelete.type === 'builder' ? 'Ban User' : 'Delete Generator'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="admin-overview">
          {/* Config Section */}
          <section className="admin-section">
            <h3>⚙️ Configuration</h3>
            <table className="admin-table compact">
              <tbody>
                <tr><td>Matchmaking Policy</td><td><code>{adminStats.config.matchmaking_policy}</code></td></tr>
                <tr><td>Initial Rating</td><td>{adminStats.config.initial_rating}</td></tr>
                <tr><td>Initial RD</td><td>{adminStats.config.initial_rd}</td></tr>
                <tr><td>Min Games for Significance</td><td>{adminStats.config.min_games_for_significance}</td></tr>
                <tr><td>Target Battles per Pair</td><td>{adminStats.config.target_battles_per_pair}</td></tr>
                <tr><td>Rating Similarity Sigma</td><td>{adminStats.config.rating_similarity_sigma}</td></tr>
                <tr><td>Quality Bias Strength</td><td>{adminStats.config.quality_bias_strength}</td></tr>
              </tbody>
            </table>
          </section>

          {/* Matchmaking Stats */}
          <section className="admin-section">
            <h3>📊 Matchmaking Statistics</h3>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-value">{adminStats.matchmaking.total_generators}</div>
                <div className="stat-label">Generators</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{adminStats.matchmaking.pairs_with_battles}/{adminStats.matchmaking.total_possible_pairs}</div>
                <div className="stat-label">Pairs with Battles</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{adminStats.matchmaking.coverage_percent.toFixed(1)}%</div>
                <div className="stat-label">Coverage</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{adminStats.matchmaking.pairs_at_target}</div>
                <div className="stat-label">Pairs at Target ({adminStats.config.target_battles_per_pair}+)</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{adminStats.matchmaking.average_rd.toFixed(0)}</div>
                <div className="stat-label">Avg Rating Deviation</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{adminStats.matchmaking.new_generators_count}</div>
                <div className="stat-label">New Generators (&lt;{adminStats.config.min_games_for_significance} games)</div>
              </div>
            </div>
          </section>

          {/* Generator List */}
          <section className="admin-section">
            <h3>🎮 Generators</h3>
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Generator</th>
                  <th>Rating</th>
                  <th>RD</th>
                  <th>Games</th>
                  <th>W/L/T</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {adminStats.generators.map((gen) => (
                  <tr key={gen.generator_id} className={gen.needs_more_games ? 'highlight' : ''}>
                    <td title={gen.generator_id}>{gen.name.substring(0, 30)}{gen.name.length > 30 ? '...' : ''}</td>
                    <td>{gen.rating.toFixed(0)}</td>
                    <td>{gen.rd.toFixed(0)}</td>
                    <td>{gen.games_played}</td>
                    <td>{gen.wins}/{gen.losses}/{gen.ties}</td>
                    <td>{gen.needs_more_games ? '🆕 Needs games' : '✓ Converged'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </div>
      )}

      {/* Confusion Matrix Tab */}
      {activeTab === 'matrix' && confusionMatrix && (
        <div className="admin-matrix">
          <section className="admin-section">
            <h3>📈 Confusion Matrix</h3>
            <p className="section-description">
              Shows win rates between generator pairs. Cell shows row-generator's win rate against column-generator.
            </p>
            
            {/* Coverage summary */}
            <div className="coverage-summary">
              <span>Coverage: {confusionMatrix.coverage.pairs_with_data}/{confusionMatrix.coverage.total_pairs} pairs</span>
              <span>({confusionMatrix.coverage.coverage_percent.toFixed(1)}%)</span>
              <span className="separator">|</span>
              <span>At target ({confusionMatrix.coverage.target_battles_per_pair}+ battles): {confusionMatrix.coverage.pairs_at_target} pairs</span>
            </div>

            {/* Matrix */}
            <div className="matrix-container">
              <table className="confusion-matrix">
                <thead>
                  <tr>
                    <th></th>
                    {confusionMatrix.generators.map((gen) => (
                      <th key={gen.id} title={gen.name}>
                        {gen.id.substring(0, 8)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {confusionMatrix.generators.map((rowGen, rowIdx) => (
                    <tr key={rowGen.id}>
                      <th title={rowGen.name}>{rowGen.id.substring(0, 8)}</th>
                      {confusionMatrix.matrix[rowIdx].map((cell, colIdx) => (
                        <td 
                          key={colIdx} 
                          className={getMatrixCellClass(cell)}
                          title={getCellTooltip(cell, rowGen.name, confusionMatrix.generators[colIdx].name)}
                        >
                          {cell === null ? '—' : (
                            cell.battles === 0 ? '∅' : (
                              cell.win_rate !== null ? `${(cell.win_rate * 100).toFixed(0)}%` : '—'
                            )
                          )}
                          {cell && cell.battles > 0 && (
                            <span className="battle-count">{cell.battles}</span>
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            <div className="matrix-legend">
              <span className="legend-item"><span className="cell win-high"></span> &gt;60% win</span>
              <span className="legend-item"><span className="cell balanced"></span> ~50%</span>
              <span className="legend-item"><span className="cell loss-high"></span> &lt;40% win</span>
              <span className="legend-item"><span className="cell empty"></span> No data</span>
            </div>
          </section>
        </div>
      )}

      {/* Coverage Gaps Tab */}
      {activeTab === 'gaps' && (
        <div className="admin-gaps">
          {/* Under-covered pairs */}
          <section className="admin-section">
            <h3>⚠️ Under-covered Pairs</h3>
            <p className="section-description">
              Pairs with fewer than {adminStats.config.target_battles_per_pair} battles.
            </p>
            {adminStats.coverage_gaps.under_covered_pairs.length === 0 ? (
              <p className="no-data">No under-covered pairs! All pairs have enough battles.</p>
            ) : (
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Generator 1</th>
                    <th>Generator 2</th>
                    <th>Battles</th>
                    <th>Needed</th>
                  </tr>
                </thead>
                <tbody>
                  {adminStats.coverage_gaps.under_covered_pairs.map((pair, idx) => (
                    <tr key={idx}>
                      <td>{pair.gen1}</td>
                      <td>{pair.gen2}</td>
                      <td>{pair.battles}</td>
                      <td>{adminStats.config.target_battles_per_pair - pair.battles}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>

          {/* Missing pairs */}
          <section className="admin-section">
            <h3>❌ Missing Pairs (No Battles)</h3>
            <p className="section-description">
              Pairs that have never been matched. Total: {adminStats.coverage_gaps.total_missing}
            </p>
            {adminStats.coverage_gaps.missing_pairs.length === 0 ? (
              <p className="no-data">No missing pairs! All generator pairs have been matched.</p>
            ) : (
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Generator 1</th>
                    <th>Generator 2</th>
                  </tr>
                </thead>
                <tbody>
                  {adminStats.coverage_gaps.missing_pairs.map((pair, idx) => (
                    <tr key={idx}>
                      <td>{pair.gen1}</td>
                      <td>{pair.gen2}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            {adminStats.coverage_gaps.total_missing > 20 && (
              <p className="more-count">... and {adminStats.coverage_gaps.total_missing - 20} more</p>
            )}
          </section>
        </div>
      )}

      {/* Data Export Tab (Stage 5) */}
      {activeTab === 'export' && (
        <div className="admin-export">
          <section className="admin-section">
            <h3>📦 Research Data Export</h3>
            <p className="section-description">
              Export raw data for research analysis. Data includes votes, trajectories, and player profiles.
            </p>
            
            {exportStatus && (
              <div className="export-status">{exportStatus}</div>
            )}
            
            <div className="export-grid">
              <div className="export-card">
                <h4>📊 Votes Export</h4>
                <p>All vote records with full telemetry data including trajectories and events.</p>
                <button 
                  onClick={() => downloadExport('votes')}
                  className="export-btn"
                >
                  Download Votes JSON
                </button>
              </div>
              
              <div className="export-card">
                <h4>🗺️ Trajectories Export</h4>
                <p>Player movement paths and death locations for heatmap analysis.</p>
                <button 
                  onClick={() => downloadExport('trajectories')}
                  className="export-btn"
                >
                  Download Trajectories JSON
                </button>
              </div>
              
              <div className="export-card">
                <h4>📈 Level Stats Export</h4>
                <p>Aggregate statistics and structural features for all levels.</p>
                <button 
                  onClick={() => downloadExport('level-stats')}
                  className="export-btn"
                >
                  Download Level Stats JSON
                </button>
              </div>
              
              <div className="export-card">
                <h4>👥 Player Profiles Export</h4>
                <p>Anonymous player preference patterns for clustering analysis.</p>
                <button 
                  onClick={() => downloadExport('player-profiles')}
                  className="export-btn"
                >
                  Download Profiles JSON
                </button>
              </div>
            </div>

            <div className="export-actions">
              <h4>Admin Actions</h4>
              <button 
                onClick={triggerFeatureExtraction}
                className="action-btn"
              >
                Extract Level Features
              </button>
              <span className="action-hint">
                Computes structural features for all levels that don't have them yet.
              </span>
            </div>
          </section>
        </div>
      )}

      {/* Builders Tab */}
      {activeTab === 'builders' && (
        <div className="admin-builders">
          <section className="admin-section">
            <h3>👥 Registered Builders ({builders.length})</h3>
            <p className="section-description">
              All registered users sorted by their best generator rating.
            </p>
            {builders.length === 0 ? (
              <p className="no-data">No registered builders yet.</p>
            ) : (
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th># Generators</th>
                    <th>Generator Names</th>
                    <th>Best Rating</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {builders.map((builder) => (
                    <tr key={builder.user_id}>
                      <td>{builder.display_name}</td>
                      <td>{builder.email}</td>
                      <td>{builder.generator_count}</td>
                      <td>
                        {builder.generator_names.length > 0 
                          ? builder.generator_names.join(', ')
                          : <span className="dim">None</span>
                        }
                      </td>
                      <td className={builder.best_rating > 0 ? 'rating-value' : 'dim'}>
                        {builder.best_rating > 0 ? Math.round(builder.best_rating) : '—'}
                      </td>
                      <td>
                        <button 
                          className="ban-btn"
                          onClick={() => setConfirmDelete({ 
                            type: 'builder', 
                            id: builder.user_id, 
                            name: builder.email 
                          })}
                        >
                          Ban
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        </div>
      )}

      {/* Generators Tab */}
      {activeTab === 'generators' && (
        <div className="admin-generators-tab">
          <section className="admin-section">
            <h3>🎮 All Generators ({allGenerators.length})</h3>
            <p className="section-description">
              All generators sorted by rating. Inactive generators are shown at the bottom.
            </p>
            {allGenerators.length === 0 ? (
              <p className="no-data">No generators found.</p>
            ) : (
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Generator Name</th>
                    <th>Builder Email</th>
                    <th>Builder Name</th>
                    <th>Rating</th>
                    <th>Games</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {allGenerators.map((gen) => (
                    <tr key={gen.generator_id} className={!gen.is_active ? 'inactive-row' : ''}>
                      <td>
                        <Link to={`/generator/${gen.generator_id}`} className="generator-link">
                          {gen.name}
                        </Link>
                      </td>
                      <td className={!gen.owner_id ? 'dim' : ''}>{gen.owner_email}</td>
                      <td className={!gen.owner_id ? 'dim' : ''}>{gen.owner_name}</td>
                      <td className="rating-value">{Math.round(gen.rating)}</td>
                      <td>{gen.games_played}</td>
                      <td>
                        {gen.is_active 
                          ? <span className="status-active">Active</span>
                          : <span className="status-inactive">Inactive</span>
                        }
                      </td>
                      <td>
                        {gen.is_active && (
                          <button 
                            className="delete-btn"
                            onClick={() => setConfirmDelete({ 
                              type: 'generator', 
                              id: gen.generator_id, 
                              name: gen.name 
                            })}
                          >
                            Delete
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        </div>
      )}
    </div>
  );

  async function executeDelete(type: 'builder' | 'generator', id: string) {
    try {
      const endpoint = type === 'builder' 
        ? `${API_BASE_URL}/v1/admin/builders/${id}`
        : `${API_BASE_URL}/v1/admin/generators/${id}`;
      
      const response = await fetch(endpoint, {
        method: 'DELETE',
        credentials: 'include',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error?.message || 'Delete failed');
      }
      
      // Refresh data
      if (type === 'builder') {
        setBuilders(prev => prev.filter(b => b.user_id !== id));
      } else {
        setAllGenerators(prev => prev.filter(g => g.generator_id !== id));
      }
      
      setConfirmDelete(null);
    } catch (err) {
      console.error('Delete failed:', err);
      alert(`Failed to delete: ${err instanceof Error ? err.message : 'Unknown error'}`);
      setConfirmDelete(null);
    }
  }

  async function downloadExport(type: 'votes' | 'trajectories' | 'level-stats' | 'player-profiles') {
    try {
      setExportStatus(`Downloading ${type}...`);
      const response = await fetch(`${API_BASE_URL}/v1/admin/export/${type}`, {
        credentials: 'include',
      });
      
      if (!response.ok) {
        throw new Error(`Export failed: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Create download
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `pcg-arena-${type}-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      setExportStatus(`✅ Downloaded ${type} (${data.total || data.data?.length || 0} records)`);
      setTimeout(() => setExportStatus(null), 3000);
    } catch (err) {
      console.error('Export failed:', err);
      setExportStatus(`❌ Export failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  }

  async function triggerFeatureExtraction() {
    try {
      setExportStatus('Extracting features...');
      const response = await fetch(`${API_BASE_URL}/v1/admin/extract-features`, {
        method: 'POST',
        credentials: 'include',
      });
      
      if (!response.ok) {
        throw new Error(`Extraction failed: ${response.status}`);
      }
      
      const data = await response.json();
      setExportStatus(`✅ ${data.message}`);
      setTimeout(() => setExportStatus(null), 3000);
    } catch (err) {
      console.error('Feature extraction failed:', err);
      setExportStatus(`❌ Failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  }
}

function getMatrixCellClass(cell: { battles: number; win_rate: number | null } | null): string {
  if (cell === null) return 'diagonal';
  if (cell.battles === 0) return 'empty';
  if (cell.win_rate === null) return 'no-rate';
  if (cell.win_rate >= 0.6) return 'win-high';
  if (cell.win_rate <= 0.4) return 'loss-high';
  return 'balanced';
}

function getCellTooltip(
  cell: { battles: number; wins: number; losses: number; ties: number; win_rate: number | null } | null,
  rowName: string,
  colName: string
): string {
  if (cell === null) return '';
  if (cell.battles === 0) return `${rowName} vs ${colName}: No battles yet`;
  return `${rowName} vs ${colName}\nBattles: ${cell.battles}\nWins: ${cell.wins}, Losses: ${cell.losses}, Ties: ${cell.ties}\nWin Rate: ${cell.win_rate !== null ? (cell.win_rate * 100).toFixed(1) + '%' : 'N/A'}`;
}

