import { useState, useCallback } from 'react';
import { ArenaApiClient } from '../api/client';
import type { Battle, LevelTelemetry, LeaderboardPreview } from '../api/types';
import { GameCanvas, GameResult } from './GameCanvas';
import { VotingPanel, VoteData } from './VotingPanel';
import { Leaderboard } from './Leaderboard';

interface BattleFlowProps {
  apiClient: ArenaApiClient;
}

type BattlePhase =
  | 'welcome'
  | 'loading'
  | 'play-left'
  | 'play-right'
  | 'voting'
  | 'submitting'
  | 'results';

export function BattleFlow({ apiClient }: BattleFlowProps) {
  const [sessionId] = useState(() => crypto.randomUUID());
  const [battle, setBattle] = useState<Battle | null>(null);
  const [phase, setPhase] = useState<BattlePhase>('welcome');
  const [error, setError] = useState<string | null>(null);
  const [leftResult, setLeftResult] = useState<GameResult | null>(null);
  const [rightResult, setRightResult] = useState<GameResult | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardPreview | null>(null);
  const [revealNames, setRevealNames] = useState(false);

  const fetchNextBattle = async () => {
    setPhase('loading');
    setError(null);
    setLeftResult(null);
    setRightResult(null);
    setRevealNames(false);

    try {
      const response = await apiClient.nextBattle(sessionId);
      setBattle(response.battle);
      console.log('Battle loaded:', response.battle.battle_id);
      setPhase('play-left');
    } catch (err) {
      console.error('Failed to fetch battle:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch battle');
      setPhase('welcome');
    }
  };

  const handleLeftFinish = useCallback((result: GameResult) => {
    console.log('Left level finished:', result);
    setLeftResult(result);
    setPhase('play-right');
  }, []);

  const handleRightFinish = useCallback((result: GameResult) => {
    console.log('Right level finished:', result);
    setRightResult(result);
    setPhase('voting');
  }, []);

  const handleVote = async (vote: VoteData) => {
    if (!battle || !leftResult || !rightResult) return;

    setPhase('submitting');
    setRevealNames(true); // Reveal names after voting

    try {
      const leftTelemetry: LevelTelemetry = {
        played: true,
        duration_seconds: leftResult.duration,
        completed: leftResult.completed,
        deaths: leftResult.deaths,
        coins_collected: leftResult.coins,
        powerups_collected: 0,
        enemies_killed: 0,
      };

      const rightTelemetry: LevelTelemetry = {
        played: true,
        duration_seconds: rightResult.duration,
        completed: rightResult.completed,
        deaths: rightResult.deaths,
        coins_collected: rightResult.coins,
        powerups_collected: 0,
        enemies_killed: 0,
      };

      const response = await apiClient.submitVote(
        sessionId,
        battle.battle_id,
        vote.result,
        vote.leftTags,
        vote.rightTags,
        { left: leftTelemetry, right: rightTelemetry }
      );

      setLeaderboard(response.leaderboard_preview);
      setPhase('results');
    } catch (err) {
      console.error('Failed to submit vote:', err);
      setError(err instanceof Error ? err.message : 'Failed to submit vote');
      setPhase('voting');
    }
  };

  const handleNextBattle = () => {
    setBattle(null);
    setLeftResult(null);
    setRightResult(null);
    setLeaderboard(null);
    setRevealNames(false);
    fetchNextBattle();
  };

  // Welcome screen
  if (phase === 'welcome') {
    return (
      <div className="battle-flow">
        <div className="welcome-state">
          <h2>Welcome to PCG Arena</h2>
          <p>Play two Mario levels side by side, then vote for your favorite!</p>
          {error && <p className="error-message">{error}</p>}
          <button onClick={fetchNextBattle} className="primary-button">
            Start Battle
          </button>
        </div>
      </div>
    );
  }

  // Loading
  if (phase === 'loading') {
    return (
      <div className="battle-flow">
        <div className="welcome-state">
          <p>Loading battle...</p>
        </div>
      </div>
    );
  }

  if (!battle) {
    return (
      <div className="battle-flow">
        <div className="error-state">
          <p className="error-message">Battle data missing</p>
          <button onClick={() => setPhase('welcome')}>Back</button>
        </div>
      </div>
    );
  }

  // Gameplay phases - side by side layout
  if (phase === 'play-left' || phase === 'play-right') {
    return (
      <div className="battle-flow">
        <div className="battle-header">
          <h2>Battle Mode</h2>
          <p className="controls-hint">Controls: Arrow Keys = Move, S = Jump, A = Run/Fire</p>
        </div>

        <div className="battle-screen">
          {/* LEFT Level */}
          <div className={`level-panel ${phase === 'play-left' ? 'active' : 'done'}`}>
            <div className="level-header">
              <span className="level-label">LEFT</span>
              {revealNames ? (
                <span className="generator-name">{battle.left.generator.name}</span>
              ) : (
                <span className="generator-hidden">Generator ???</span>
              )}
            </div>
            <GameCanvas
              level={battle.left.level_payload.tilemap}
              timeLimit={battle.presentation.suggested_time_limit_seconds}
              isActive={phase === 'play-left'}
              onFinish={handleLeftFinish}
            />
            <div className="level-status">
              {leftResult ? (
                <span className="status-complete">
                  ✓ {leftResult.completed ? 'WIN' : 'LOSE'} | {leftResult.coins} coins
                </span>
              ) : phase === 'play-left' ? (
                <span className="status-playing">▶ PLAYING NOW</span>
              ) : (
                <span className="status-waiting">Waiting...</span>
              )}
            </div>
          </div>

          {/* RIGHT Level */}
          <div className={`level-panel ${phase === 'play-right' ? 'active' : ''} ${rightResult ? 'done' : ''}`}>
            <div className="level-header">
              <span className="level-label">RIGHT</span>
              {revealNames ? (
                <span className="generator-name">{battle.right.generator.name}</span>
              ) : (
                <span className="generator-hidden">Generator ???</span>
              )}
            </div>
            <GameCanvas
              level={battle.right.level_payload.tilemap}
              timeLimit={battle.presentation.suggested_time_limit_seconds}
              isActive={phase === 'play-right'}
              onFinish={handleRightFinish}
            />
            <div className="level-status">
              {rightResult ? (
                <span className="status-complete">
                  ✓ {rightResult.completed ? 'WIN' : 'LOSE'} | {rightResult.coins} coins
                </span>
              ) : phase === 'play-right' ? (
                <span className="status-playing">▶ PLAYING NOW</span>
              ) : leftResult ? (
                <span className="status-next">Next...</span>
              ) : (
                <span className="status-waiting">Waiting...</span>
              )}
            </div>
          </div>
        </div>

        <div className="battle-footer">
          <p>
            {phase === 'play-left'
              ? 'Play the LEFT level. When finished, the RIGHT level will start.'
              : 'Play the RIGHT level. Then you can vote!'}
          </p>
        </div>
      </div>
    );
  }

  // Voting phase
  if (phase === 'voting' || phase === 'submitting') {
    return (
      <div className="battle-flow">
        <div className="battle-header">
          <h2>Vote for Your Favorite</h2>
          <p>Which level did you enjoy more?</p>
        </div>

        <div className="battle-screen voting-view">
          {/* LEFT Level Summary */}
          <div className="level-panel done">
            <div className="level-header">
              <span className="level-label">LEFT</span>
              <span className="generator-hidden">Generator ???</span>
            </div>
            <div className="level-summary">
              {leftResult && (
                <>
                  <p>{leftResult.completed ? '✓ Completed' : '✗ Failed'}</p>
                  <p>Coins: {leftResult.coins}</p>
                  <p>Time: {leftResult.duration.toFixed(1)}s</p>
                </>
              )}
            </div>
          </div>

          {/* RIGHT Level Summary */}
          <div className="level-panel done">
            <div className="level-header">
              <span className="level-label">RIGHT</span>
              <span className="generator-hidden">Generator ???</span>
            </div>
            <div className="level-summary">
              {rightResult && (
                <>
                  <p>{rightResult.completed ? '✓ Completed' : '✗ Failed'}</p>
                  <p>Coins: {rightResult.coins}</p>
                  <p>Time: {rightResult.duration.toFixed(1)}s</p>
                </>
              )}
            </div>
          </div>
        </div>

        {phase === 'voting' ? (
          <VotingPanel onVote={handleVote} />
        ) : (
          <div className="submitting-state">
            <p>Submitting vote...</p>
          </div>
        )}
        {error && <p className="error-message">{error}</p>}
      </div>
    );
  }

  // Results phase - reveal generator names
  if (phase === 'results' && leaderboard) {
    return (
      <div className="battle-flow">
        <div className="results-header">
          <h2>Vote Submitted!</h2>
          <p>Generator names revealed:</p>
        </div>

        <div className="generator-reveal">
          <div className="reveal-panel">
            <span className="reveal-label">LEFT:</span>
            <span className="reveal-name">{battle.left.generator.name}</span>
          </div>
          <div className="reveal-panel">
            <span className="reveal-label">RIGHT:</span>
            <span className="reveal-name">{battle.right.generator.name}</span>
          </div>
        </div>

        <Leaderboard data={leaderboard} isPreview={true} />

        <button onClick={handleNextBattle} className="primary-button">
          Next Battle
        </button>
      </div>
    );
  }

  return null;
}
