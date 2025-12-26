import type { LeaderboardPreview, LeaderboardResponse } from '../api/types';

interface LeaderboardProps {
  data: LeaderboardPreview | LeaderboardResponse;
  isPreview?: boolean;
}

export function Leaderboard({ data, isPreview = false }: LeaderboardProps) {
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
            {generators.map((gen, index) => (
              <tr key={gen.generator_id}>
                <td>{'rank' in gen ? gen.rank : index + 1}</td>
                <td className="generator-name">{gen.name}</td>
                <td>{gen.rating.toFixed(0)}</td>
                <td>{gen.games_played}</td>
                {'wins' in gen && (
                  <>
                    <td>{gen.wins}</td>
                    <td>{gen.losses}</td>
                    <td>{gen.ties}</td>
                  </>
                )}
              </tr>
            ))}
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

