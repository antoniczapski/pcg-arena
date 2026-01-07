import { useState, useCallback, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
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
  | 'results'
  | 'practice-complete';  // New phase for practice mode

export function BattleFlow({ apiClient }: BattleFlowProps) {
  const [searchParams, setSearchParams] = useSearchParams();
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
  const [isPracticeMode, setIsPracticeMode] = useState(false);
  const battleHeaderRef = useRef<HTMLDivElement>(null);

  // Scroll to battle when starting
  useEffect(() => {
    if (phase === 'play-left' && battleHeaderRef.current) {
      setTimeout(() => {
        battleHeaderRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    }
  }, [phase]);

  // Check for practice mode on mount
  useEffect(() => {
    const practiceLevel = searchParams.get('practice');
    if (practiceLevel) {
      startPracticeBattle(practiceLevel);
    }
  }, []);

  const startPracticeBattle = async (levelId: string) => {
    setPhase('loading');
    setError(null);
    setLeftResult(null);
    setRightResult(null);
    setRevealNames(true);  // Always reveal generator name in practice mode
    setLeftTags([]);
    setRightTags([]);
    setIsPracticeMode(true);

    try {
      const response = await apiClient.createPracticeBattle(sessionId, levelId, playerId);
      setBattle(response.battle);
      console.log('Practice battle loaded:', response.battle.battle_id, 'level:', levelId);
      setPhase('play-left');
    } catch (err) {
      console.error('Failed to create practice battle:', err);
      setError(err instanceof Error ? err.message : 'Failed to create practice battle');
      setPhase('welcome');
    }
  };

  // Handle practice-complete phase: submit trajectories then start regular battle
  useEffect(() => {
    if (phase === 'practice-complete' && battle && leftResult && rightResult) {
      const completePractice = async () => {
        try {
          // Build telemetry for practice battle
          const leftTelemetry: LevelTelemetry = {
            played: !leftResult.skipped,
            skipped: leftResult.skipped,
            duration_seconds: leftResult.duration,
            completed: leftResult.completed,
            deaths: leftResult.deaths,
            coins_collected: leftResult.coins,
            powerups_collected: leftResult.powerupsMushroom + leftResult.powerupsFlower,
            enemies_killed: leftResult.enemiesStomped + leftResult.enemiesFireKilled + leftResult.enemiesShellKilled,
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
            played: !rightResult.skipped,
            skipped: rightResult.skipped,
            duration_seconds: rightResult.duration,
            completed: rightResult.completed,
            deaths: rightResult.deaths,
            coins_collected: rightResult.coins,
            powerups_collected: rightResult.powerupsMushroom + rightResult.powerupsFlower,
            enemies_killed: rightResult.enemiesStomped + rightResult.enemiesFireKilled + rightResult.enemiesShellKilled,
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

          // Submit practice completion with trajectories
          await apiClient.completePracticeBattle(
            sessionId,
            battle.battle_id,
            { left: leftTelemetry, right: rightTelemetry },
            playerId
          );

          console.log('Practice battle completed, starting regular battle');
          
          // Clear practice mode and URL parameter
          setIsPracticeMode(false);
          setSearchParams({});
          
          // Start regular battle
          fetchNextBattle();
        } catch (err) {
          console.error('Failed to complete practice battle:', err);
          // Even if practice submission fails, still start regular battle
          setIsPracticeMode(false);
          setSearchParams({});
          fetchNextBattle();
        }
      };

      completePractice();
    }
  }, [phase, battle, leftResult, rightResult]);

  // Auto-advance from results phase after 3 seconds (or on key press)
  useEffect(() => {
    if (phase === 'results') {
      let skipped = false;

      const handleKeyPress = () => {
        if (!skipped) {
          skipped = true;
          fetchNextBattle();
        }
      };

      const timer = setTimeout(() => {
        if (!skipped) {
          fetchNextBattle();
        }
      }, 3000);

      window.addEventListener('keydown', handleKeyPress);

      return () => {
        clearTimeout(timer);
        window.removeEventListener('keydown', handleKeyPress);
      };
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
    // In practice mode, skip voting and go directly to practice-complete
    if (isPracticeMode) {
      setPhase('practice-complete');
    } else {
      setPhase('voting');
    }
  }, [isPracticeMode]);

  // Skip handlers for levels
  const handleSkipLeft = useCallback(() => {
    if (!battle) return;
    console.log('Left level skipped');
    const skippedResult: GameResult = {
      status: 0 as any, // Not used for skipped
      coins: 0,
      deaths: 0,
      duration: 0,
      completed: false,
      skipped: true,
      levelId: battle.left.level_id,
      jumps: 0,
      enemiesStomped: 0,
      enemiesFireKilled: 0,
      enemiesShellKilled: 0,
      powerupsMushroom: 0,
      powerupsFlower: 0,
      livesCollected: 0,
      trajectory: [],
      deathLocations: [],
      events: [],
    };
    setLeftResult(skippedResult);
    setPhase('play-right');
  }, [battle]);

  const handleSkipRight = useCallback(() => {
    if (!battle) return;
    console.log('Right level skipped');
    const skippedResult: GameResult = {
      status: 0 as any, // Not used for skipped
      coins: 0,
      deaths: 0,
      duration: 0,
      completed: false,
      skipped: true,
      levelId: battle.right.level_id,
      jumps: 0,
      enemiesStomped: 0,
      enemiesFireKilled: 0,
      enemiesShellKilled: 0,
      powerupsMushroom: 0,
      powerupsFlower: 0,
      livesCollected: 0,
      trajectory: [],
      deathLocations: [],
      events: [],
    };
    setRightResult(skippedResult);
    // In practice mode, skip voting and go directly to practice-complete
    if (isPracticeMode) {
      setPhase('practice-complete');
    } else {
      setPhase('voting');
    }
  }, [battle, isPracticeMode]);

  const handleVote = async (vote: VoteData) => {
    if (!battle || !leftResult || !rightResult) return;

    setPhase('submitting');
    setRevealNames(true); // Reveal names after voting

    try {
      // Stage 5: Build enhanced telemetry from GameResult
      const leftTelemetry: LevelTelemetry = {
        played: !leftResult.skipped,
        skipped: leftResult.skipped,
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
        played: !rightResult.skipped,
        skipped: rightResult.skipped,
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
          <p>{isPracticeMode ? 'Loading practice level...' : 'Loading battle...'}</p>
        </div>
      </div>
    );
  }

  // Practice complete - transitional state
  if (phase === 'practice-complete') {
    return (
      <div className="battle-flow">
        <div className="welcome-state">
          <h2>Practice Complete!</h2>
          <p>Starting regular battle...</p>
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
        <div className="battle-header" ref={battleHeaderRef}>
          <h2>{isPracticeMode ? 'Practice Mode' : 'Battle Mode'}</h2>
          {isPracticeMode && <p className="practice-hint">Playing the same level on both sides. No voting required.</p>}
          <p className="controls-hint">Controls: Arrow Keys = Move, S = Jump, A = Run/Fire</p>
        </div>

        <div className="battle-screen">
          {/* LEFT Level */}
          <div className={`level-panel ${phase === 'play-left' ? 'active' : 'done'}`}>
            <div className="level-header">
              <span className="level-label">LEFT</span>
              {phase === 'play-left' && !leftResult ? (
                <button className="skip-button" onClick={handleSkipLeft}>Skip →</button>
              ) : revealNames ? (
                <span className="generator-name">{battle.left.generator.name}</span>
              ) : null}
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
                  ✓ {leftResult.skipped ? 'SKIPPED' : leftResult.completed ? 'WIN' : 'LOSE'} {!leftResult.skipped && `| ${leftResult.coins} coins`}
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
              {phase === 'play-right' && !rightResult ? (
                <button className="skip-button" onClick={handleSkipRight}>Skip →</button>
              ) : revealNames ? (
                <span className="generator-name">{battle.right.generator.name}</span>
              ) : null}
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
                  ✓ {rightResult.skipped ? 'SKIPPED' : rightResult.completed ? 'WIN' : 'LOSE'} {!rightResult.skipped && `| ${rightResult.coins} coins`}
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
            <p className="auto-advance-hint">Loading next battle... (press any key to skip)</p>
          </div>
        )}
        {error && <p className="error-message">{error}</p>}
      </div>
    );
  }

  return null;
}
