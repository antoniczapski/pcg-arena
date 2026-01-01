import { useState, useCallback, useEffect } from 'react';
import { ArenaApiClient } from '../api/client';
import type { Battle, LevelTelemetry } from '../api/types';
import { GameCanvas, GameResult } from './GameCanvas';
import { VotingPanel, VoteData } from './VotingPanel';
import { LevelPreview } from './LevelPreview';
import { TaggableLevelPreview } from './TagSelector';
import { getOrCreatePlayerId } from '../utils/playerId';


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
  const [playerId] = useState(() => getOrCreatePlayerId()); // Stage 5: Persistent player ID
  const [battle, setBattle] = useState<Battle | null>(null);
  const [phase, setPhase] = useState<BattlePhase>('welcome');
  const [error, setError] = useState<string | null>(null);
  const [leftResult, setLeftResult] = useState<GameResult | null>(null);
  const [rightResult, setRightResult] = useState<GameResult | null>(null);
  const [revealNames, setRevealNames] = useState(false);
  const [leftTags, setLeftTags] = useState<string[]>([]);
  const [rightTags, setRightTags] = useState<string[]>([]);

  // Auto-advance from results phase after 3 seconds
  useEffect(() => {
    if (phase === 'results') {
      const timer = setTimeout(() => {
        fetchNextBattle();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [phase]);

  const fetchNextBattle = async () => {
    setPhase('loading');
    setError(null);
    setLeftResult(null);
    setRightResult(null);
    setRevealNames(false);
    setLeftTags([]);
    setRightTags([]);

    try {
      const response = await apiClient.nextBattle(sessionId, playerId);
      setBattle(response.battle);
      console.log('Battle loaded:', response.battle.battle_id, 'player:', playerId);
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
      // Stage 5: Build enhanced telemetry from GameResult
      const leftTelemetry: LevelTelemetry = {
        played: true,
        duration_seconds: leftResult.duration,
        completed: leftResult.completed,
        deaths: leftResult.deaths,
        coins_collected: leftResult.coins,
        powerups_collected: leftResult.powerupsMushroom + leftResult.powerupsFlower,
        enemies_killed: leftResult.enemiesStomped + leftResult.enemiesFireKilled + leftResult.enemiesShellKilled,
        // Stage 5: Enhanced fields
        level_id: leftResult.levelId,
        jumps: leftResult.jumps,
        enemies_stomped: leftResult.enemiesStomped,
        enemies_fire_killed: leftResult.enemiesFireKilled,
        enemies_shell_killed: leftResult.enemiesShellKilled,
        powerups_mushroom: leftResult.powerupsMushroom,
        powerups_flower: leftResult.powerupsFlower,
        lives_collected: leftResult.livesCollected,
        trajectory: leftResult.trajectory,
        death_locations: leftResult.deathLocations,
        events: leftResult.events,
      };

      const rightTelemetry: LevelTelemetry = {
        played: true,
        duration_seconds: rightResult.duration,
        completed: rightResult.completed,
        deaths: rightResult.deaths,
        coins_collected: rightResult.coins,
        powerups_collected: rightResult.powerupsMushroom + rightResult.powerupsFlower,
        enemies_killed: rightResult.enemiesStomped + rightResult.enemiesFireKilled + rightResult.enemiesShellKilled,
        // Stage 5: Enhanced fields
        level_id: rightResult.levelId,
        jumps: rightResult.jumps,
        enemies_stomped: rightResult.enemiesStomped,
        enemies_fire_killed: rightResult.enemiesFireKilled,
        enemies_shell_killed: rightResult.enemiesShellKilled,
        powerups_mushroom: rightResult.powerupsMushroom,
        powerups_flower: rightResult.powerupsFlower,
        lives_collected: rightResult.livesCollected,
        trajectory: rightResult.trajectory,
        death_locations: rightResult.deathLocations,
        events: rightResult.events,
      };

      await apiClient.submitVote(
        sessionId,
        battle.battle_id,
        vote.result,
        vote.leftTags,
        vote.rightTags,
        { left: leftTelemetry, right: rightTelemetry },
        playerId  // Stage 5: Include player ID
      );

      setPhase('results');
    } catch (err) {
      console.error('Failed to submit vote:', err);
      setError(err instanceof Error ? err.message : 'Failed to submit vote');
      setPhase('voting');
    }
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
              levelId={battle.left.level_id}
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
              levelId={battle.right.level_id}
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

  // Voting phase (includes results reveal on same page)
  if (phase === 'voting' || phase === 'submitting' || phase === 'results') {
    // Tilemap is plain UTF-8 text, not base64 encoded
    const leftTilemap = battle.left.level_payload.tilemap;
    const rightTilemap = battle.right.level_payload.tilemap;
    const showResults = phase === 'results';

    return (
      <div className="battle-flow">
        <div className="battle-header">
          <h2>{showResults ? 'Vote Submitted!' : 'Vote for Your Favorite'}</h2>
          <p>{showResults ? 'Generator names revealed:' : 'Which level did you enjoy more?'}</p>
        </div>

        <div className="voting-levels-container">
          {/* Level A (was LEFT) */}
          <div className="voting-level-panel">
            <div className="voting-level-header">
              <span className="voting-level-label">Level A</span>
              {showResults && (
                <span className="voting-generator-reveal">{battle.left.generator.name}</span>
              )}
            </div>
            <div className="voting-level-preview">
              <TaggableLevelPreview
                selectedTags={leftTags}
                onTagsChange={setLeftTags}
                disabled={showResults || phase === 'submitting'}
              >
                <LevelPreview
                  levelId="level-a"
                  tilemap={leftTilemap}
                  width={battle.left.format.width}
                  height={battle.left.format.height}
                  scale={0.5}
                  showLabel={false}
                />
              </TaggableLevelPreview>
            </div>
          </div>

          {/* Level B (was RIGHT) */}
          <div className="voting-level-panel">
            <div className="voting-level-header">
              <span className="voting-level-label">Level B</span>
              {showResults && (
                <span className="voting-generator-reveal">{battle.right.generator.name}</span>
              )}
            </div>
            <div className="voting-level-preview">
              <TaggableLevelPreview
                selectedTags={rightTags}
                onTagsChange={setRightTags}
                disabled={showResults || phase === 'submitting'}
              >
                <LevelPreview
                  levelId="level-b"
                  tilemap={rightTilemap}
                  width={battle.right.format.width}
                  height={battle.right.format.height}
                  scale={0.5}
                  showLabel={false}
                />
              </TaggableLevelPreview>
            </div>
          </div>
        </div>

        <p className="tag-hint">💡 Hover over a level to add tags (optional)</p>

        {phase === 'voting' ? (
          <VotingPanel 
            onVote={handleVote} 
            useABNaming={true}
            leftTags={leftTags}
            rightTags={rightTags}
          />
        ) : phase === 'submitting' ? (
          <div className="submitting-state">
            <p>Submitting vote...</p>
          </div>
        ) : (
          <div className="results-auto-advance">
            <p className="auto-advance-hint">Loading next battle...</p>
          </div>
        )}
        {error && <p className="error-message">{error}</p>}
      </div>
    );
  }

  return null;
}
