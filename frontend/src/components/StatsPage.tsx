/**
 * Stage 5: Platform Statistics Page
 * 
 * Displays platform-wide aggregate statistics for public view.
 */

import { useState, useEffect } from 'react';
import { ArenaApiClient } from '../api/client';
import type { PlatformStatsResponse } from '../api/types';
import './StatsPage.css';

interface StatsPageProps {
  apiClient: ArenaApiClient;
}

export function StatsPage({ apiClient }: StatsPageProps) {
  const [stats, setStats] = useState<PlatformStatsResponse['stats'] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await apiClient.getPlatformStats();
        setStats(response.stats);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch stats:', err);
        setError(err instanceof Error ? err.message : 'Failed to load statistics');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [apiClient]);

  if (loading) {
    return (
      <div className="stats-page">
        <div className="stats-loading">Loading statistics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stats-page">
        <div className="stats-error">{error}</div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="stats-page">
        <div className="stats-empty">No statistics available yet.</div>
      </div>
    );
  }

  return (
    <div className="stats-page">
      <h1 className="stats-title">Platform Statistics</h1>
      
      <div className="stats-grid">
        {/* Totals Card */}
        <div className="stats-card totals-card">
          <h2>Activity Overview</h2>
          <div className="stats-metrics">
            <div className="metric">
              <span className="metric-value">{stats.totals.battles_completed.toLocaleString()}</span>
              <span className="metric-label">Battles Completed</span>
            </div>
            <div className="metric">
              <span className="metric-value">{stats.totals.votes_cast.toLocaleString()}</span>
              <span className="metric-label">Votes Cast</span>
            </div>
            <div className="metric">
              <span className="metric-value">{stats.totals.unique_players.toLocaleString()}</span>
              <span className="metric-label">Unique Players</span>
            </div>
            <div className="metric">
              <span className="metric-value">{stats.totals.active_generators}</span>
              <span className="metric-label">Active Generators</span>
            </div>
            <div className="metric">
              <span className="metric-value">{stats.totals.total_levels}</span>
              <span className="metric-label">Total Levels</span>
            </div>
          </div>
        </div>

        {/* Vote Distribution Card */}
        <div className="stats-card distribution-card">
          <h2>Vote Distribution</h2>
          <div className="vote-bars">
            <div className="vote-bar-row">
              <span className="bar-label">Left Wins</span>
              <div className="bar-container">
                <div 
                  className="bar bar-left" 
                  style={{ width: `${stats.vote_distribution.left_percent}%` }}
                />
              </div>
              <span className="bar-value">{stats.vote_distribution.left_percent}%</span>
            </div>
            <div className="vote-bar-row">
              <span className="bar-label">Right Wins</span>
              <div className="bar-container">
                <div 
                  className="bar bar-right" 
                  style={{ width: `${stats.vote_distribution.right_percent}%` }}
                />
              </div>
              <span className="bar-value">{stats.vote_distribution.right_percent}%</span>
            </div>
            <div className="vote-bar-row">
              <span className="bar-label">Ties</span>
              <div className="bar-container">
                <div 
                  className="bar bar-tie" 
                  style={{ width: `${stats.vote_distribution.tie_percent}%` }}
                />
              </div>
              <span className="bar-value">{stats.vote_distribution.tie_percent}%</span>
            </div>
            <div className="vote-bar-row">
              <span className="bar-label">Skips</span>
              <div className="bar-container">
                <div 
                  className="bar bar-skip" 
                  style={{ width: `${stats.vote_distribution.skip_percent}%` }}
                />
              </div>
              <span className="bar-value">{stats.vote_distribution.skip_percent}%</span>
            </div>
          </div>
        </div>

        {/* Engagement Card */}
        <div className="stats-card engagement-card">
          <h2>Player Engagement</h2>
          <div className="stats-metrics">
            <div className="metric large">
              <span className="metric-value">{stats.engagement.completion_rate_percent}%</span>
              <span className="metric-label">Average Completion Rate</span>
            </div>
            <div className="metric">
              <span className="metric-value">{stats.engagement.avg_deaths_per_level}</span>
              <span className="metric-label">Avg Deaths per Level</span>
            </div>
            <div className="metric">
              <span className="metric-value">{stats.engagement.avg_duration_seconds}s</span>
              <span className="metric-label">Avg Play Duration</span>
            </div>
          </div>
        </div>
      </div>

      <div className="stats-note">
        <p>Statistics are aggregated across all levels and generators. 
        Individual generator and level statistics are available on their respective pages.</p>
      </div>
    </div>
  );
}

