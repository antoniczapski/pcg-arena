import { useState, useEffect } from 'react';
import { ArenaApiClient } from '../api/client';
import type { LeaderboardResponse } from '../api/types';
import { Leaderboard } from '../components/Leaderboard';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const apiClient = new ArenaApiClient(API_BASE_URL);

export function LeaderboardPage() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await apiClient.leaderboard();
        setLeaderboard(data);
      } catch (err) {
        console.error('Failed to fetch leaderboard:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch leaderboard');
      } finally {
        setIsLoading(false);
      }
    };

    fetchLeaderboard();
  }, []);

  return (
    <div className="leaderboard-page">
      <div className="leaderboard-page-header">
        <h1>Generator Leaderboard</h1>
        <p>Rankings based on player votes using Elo rating system</p>
      </div>

      {isLoading && (
        <div className="leaderboard-loading">
          <p>Loading leaderboard...</p>
        </div>
      )}

      {error && (
        <div className="leaderboard-error">
          <p>Error: {error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Retry
          </button>
        </div>
      )}

      {leaderboard && (
        <Leaderboard data={leaderboard} isPreview={false} linkable={true} />
      )}
    </div>
  );
}

