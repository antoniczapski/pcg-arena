/**
 * GeneratorPage - Displays detailed view of a generator with all its levels
 * 
 * Accessible from:
 * - Leaderboard (clicking on a generator)
 * - Builder Profile (clicking "View" on owned generator)
 */

import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArenaApiClient } from '../api/client';
import { LevelPreviewList } from '../components/LevelPreview';
import type { GeneratorDetails, LevelPreviewData } from '../api/types';
import '../styles/generator.css';

// API base URL from environment
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export function GeneratorPage() {
  const { generatorId } = useParams<{ generatorId: string }>();
  const navigate = useNavigate();
  const [generator, setGenerator] = useState<GeneratorDetails | null>(null);
  const [levels, setLevels] = useState<LevelPreviewData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Navigate to level detail page when clicking a level
  const handleLevelClick = (levelId: string) => {
    navigate(`/level/${encodeURIComponent(levelId)}`);
  };

  useEffect(() => {
    async function fetchGenerator() {
      if (!generatorId) {
        setError('No generator ID provided');
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const apiClient = new ArenaApiClient(API_BASE_URL);
        const response = await apiClient.getGenerator(generatorId);
        setGenerator(response.generator);
        setLevels(response.levels);
      } catch (err) {
        console.error('Failed to fetch generator:', err);
        setError(err instanceof Error ? err.message : 'Failed to load generator');
      } finally {
        setIsLoading(false);
      }
    }

    fetchGenerator();
  }, [generatorId]);

  if (isLoading) {
    return (
      <div className="generator-page">
        <div className="generator-loading">
          <p>Loading generator...</p>
        </div>
      </div>
    );
  }

  if (error || !generator) {
    return (
      <div className="generator-page">
        <div className="generator-error">
          <h2>Generator Not Found</h2>
          <p>{error || 'The requested generator could not be found.'}</p>
          <Link to="/" className="back-link">← Back to Arena</Link>
        </div>
      </div>
    );
  }

  const winRate = generator.games_played > 0
    ? ((generator.wins / generator.games_played) * 100).toFixed(1)
    : '-';

  const lossRate = generator.games_played > 0
    ? ((generator.losses / generator.games_played) * 100).toFixed(1)
    : '-';

  return (
    <div className="generator-page">
      {/* Header Section */}
      <div className="generator-header">
        <Link to="/" className="back-link">← Back to Arena</Link>
        
        <div className="generator-title">
          <h1>{generator.name}</h1>
          <span className="generator-version">v{generator.version}</span>
          {!generator.is_active && (
            <span className="generator-inactive-badge">Inactive</span>
          )}
        </div>

        <code className="generator-id-display">{generator.generator_id}</code>

        {generator.description && (
          <p className="generator-description">{generator.description}</p>
        )}

        {generator.tags.length > 0 && (
          <div className="generator-tags">
            {generator.tags.map((tag) => (
              <span key={tag} className="tag">{tag}</span>
            ))}
          </div>
        )}

        {generator.documentation_url && (
          <a 
            href={generator.documentation_url}
            target="_blank"
            rel="noopener noreferrer"
            className="generator-docs-link"
          >
            📄 Documentation
          </a>
        )}
      </div>

      {/* Stats Section */}
      <div className="generator-stats-section">
        <h2>Statistics</h2>
        <div className="generator-stats-grid">
          {generator.rank && (
            <div className="stat-card highlight">
              <span className="stat-value">#{generator.rank}</span>
              <span className="stat-label">Rank</span>
            </div>
          )}
          <div className="stat-card highlight">
            <span className="stat-value">{generator.rating.toFixed(0)}</span>
            <span className="stat-label">Rating</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{generator.games_played}</span>
            <span className="stat-label">Games Played</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{generator.wins}</span>
            <span className="stat-label">Wins ({winRate}%)</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{generator.losses}</span>
            <span className="stat-label">Losses ({lossRate}%)</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{generator.ties}</span>
            <span className="stat-label">Ties</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{generator.level_count}</span>
            <span className="stat-label">Levels</span>
          </div>
        </div>
      </div>

      {/* Levels Section */}
      <div className="generator-levels-section">
        <h2>Level Gallery ({levels.length} levels)</h2>
        <p className="levels-hint">
          Click any level to view detailed statistics and death heatmap. 
          Each level is 16 tiles tall and up to 250 tiles wide.
        </p>
        
        <div className="levels-container">
          <LevelPreviewList 
            levels={levels}
            scale={1}
            onLevelClick={handleLevelClick}
          />
        </div>
      </div>

      {/* Footer info */}
      <div className="generator-meta">
        <p>Created: {new Date(generator.created_at_utc).toLocaleString()}</p>
        <p>Last Updated: {new Date(generator.updated_at_utc).toLocaleString()}</p>
      </div>
    </div>
  );
}

