import { Link } from 'react-router-dom';
import type { LeaderboardPreview, LeaderboardResponse } from '../api/types';

interface LeaderboardProps {
  data: LeaderboardPreview | LeaderboardResponse;
  isPreview?: boolean;
  /** Whether generator names should be clickable links to generator pages */
  linkable?: boolean;
}

export function Leaderboard({ data, isPreview = false, linkable = true }: LeaderboardProps) {
  const generators = 'generators' in data ? data.generators : [];

  return (
    <div className="leaderboard">
      <h2>{isPreview ? 'Leaderboard Preview' : 'Full Leaderboard'}</h2>
      
      {generators.length === 0 ? (
        <p>No generators ranked yet.</p>
      ) : (
        <table className="leaderboard-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Generator</th>
              <th>Rating</th>
              <th>Games</th>
              {'wins' in generators[0] && (
                <>
                  <th>W</th>
                  <th>L</th>
                  <th>T</th>
                </>
              )}
            </tr>
          </thead>
          <tbody>
            {generators.map((gen, index) => {
              const hasWins = 'wins' in gen;
              const ranking = gen as any; // Type narrowing for optional fields
              return (
                <tr key={gen.generator_id}>
                  <td>{'rank' in gen ? (gen as any).rank : index + 1}</td>
                  <td className="generator-name">
                    {linkable ? (
                      <Link 
                        to={`/generator/${gen.generator_id}`}
                        className="generator-link"
                      >
                        {gen.name}
                      </Link>
                    ) : (
                      gen.name
                    )}
                  </td>
                  <td>{gen.rating.toFixed(0)}</td>
                  <td>{gen.games_played}</td>
                  {hasWins && (
                    <>
                      <td>{ranking.wins}</td>
                      <td>{ranking.losses}</td>
                      <td>{ranking.ties}</td>
                    </>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
      
      {!isPreview && 'updated_at_utc' in data && (
        <p className="timestamp">
          Updated: {new Date(data.updated_at_utc).toLocaleString()}
        </p>
      )}
    </div>
  );
}

