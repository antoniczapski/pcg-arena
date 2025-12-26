import { useRef, useEffect, useState, useCallback } from 'react';
import { MarioGame } from '../engine/MarioGame';
import { MarioWorld } from '../engine/MarioWorld';
import { GameStatus } from '../engine/GameStatus';
import { KeyboardInput } from '../engine/input/KeyboardInput';
import { assetLoader } from '../engine/graphics/AssetLoader';
import { Camera } from '../engine/graphics/Camera';
import { TilemapRenderer } from '../engine/graphics/TilemapRenderer';
import { SpriteRenderer } from '../engine/graphics/SpriteRenderer';

export interface GameResult {
  status: GameStatus;
  coins: number;
  deaths: number;
  duration: number;
  completed: boolean;
}

interface GameCanvasProps {
  level: string;
  timeLimit: number;
  isActive: boolean;
  onFinish: (result: GameResult) => void;
}

export function GameCanvas({ level, timeLimit, isActive, onFinish }: GameCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [assetsLoaded, setAssetsLoaded] = useState(false);
  const [assetError, setAssetError] = useState<string | null>(null);
  const [displayState, setDisplayState] = useState<'loading' | 'ready' | 'playing' | 'finished'>('loading');
  
  const gameRef = useRef<MarioGame | null>(null);
  const inputRef = useRef<KeyboardInput | null>(null);
  const startTimeRef = useRef<number>(0);
  const deathCountRef = useRef<number>(0);
  const cameraRef = useRef<Camera | null>(null);
  const tilemapRendererRef = useRef<TilemapRenderer | null>(null);
  const spriteRendererRef = useRef<SpriteRenderer | null>(null);
  const hasStartedRef = useRef(false);

  // Store onFinish in a ref to avoid dependency issues
  const onFinishRef = useRef(onFinish);
  onFinishRef.current = onFinish;

  // Load assets on mount
  useEffect(() => {
    let mounted = true;

    const loadAssets = async () => {
      try {
        await assetLoader.loadAllAssets();
        if (mounted) {
          setAssetsLoaded(true);
          setDisplayState('ready');
        }
      } catch (err) {
        console.error('[GameCanvas] Asset loading failed:', err);
        if (mounted) {
          setAssetError(err instanceof Error ? err.message : 'Failed to load assets');
        }
      }
    };

    loadAssets();

    return () => {
      mounted = false;
    };
  }, []);

  // Draw preview when assets are loaded
  useEffect(() => {
    if (!assetsLoaded || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.imageSmoothingEnabled = false;
    
    if (!cameraRef.current) {
      cameraRef.current = new Camera(256, 256);
      tilemapRendererRef.current = new TilemapRenderer();
      spriteRendererRef.current = new SpriteRenderer();
    }

    // Create a temporary world just to render preview
    const tempWorld = new MarioWorld();
    tempWorld.visuals = true;
    tempWorld.initializeLevel(level, 1000 * timeLimit);

    // Render preview
    const camera = cameraRef.current;
    camera.follow(tempWorld.mario.x, tempWorld.mario.y, tempWorld.level.width, tempWorld.level.height);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    tempWorld.render(ctx, tilemapRendererRef.current!, spriteRendererRef.current!, camera);
  }, [assetsLoaded, level, timeLimit]);

  // Start game when active - use ref to track if started
  useEffect(() => {
    // Only start if active, assets loaded, and not already started
    if (!isActive || !assetsLoaded || hasStartedRef.current) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Mark as started
    hasStartedRef.current = true;
    setDisplayState('playing');

    // Setup input - create it fresh for this game session
    const input = new KeyboardInput();
    inputRef.current = input;

    // Create game instance
    const game = new MarioGame();
    gameRef.current = game;
    startTimeRef.current = Date.now();
    deathCountRef.current = 0;

    const camera = cameraRef.current!;
    const tilemapRenderer = tilemapRendererRef.current!;
    const spriteRenderer = spriteRendererRef.current!;

    // Start game
    game.playGame(
      level,
      timeLimit,
      0,
      30,
      () => input.getActions(),
      (world) => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        camera.follow(world.mario.x, world.mario.y, world.level.width, world.level.height);
        world.render(ctx, tilemapRenderer, spriteRenderer, camera);

        if (!world.mario.alive && world.gameStatus === GameStatus.RUNNING) {
          deathCountRef.current++;
        }
      }
    ).then((result) => {
      // Game finished - clean up input
      if (inputRef.current) {
        inputRef.current.destroy();
        inputRef.current = null;
      }

      const duration = (Date.now() - startTimeRef.current) / 1000;
      const gameResult: GameResult = {
        status: result.gameStatus,
        coins: result.world.coins,
        deaths: deathCountRef.current,
        duration,
        completed: result.gameStatus === GameStatus.WIN,
      };
      setDisplayState('finished');
      onFinishRef.current(gameResult);
    }).catch((err) => {
      console.error('[GameCanvas] Game error:', err);
    });

    // Cleanup only when component unmounts
    return () => {
      if (gameRef.current) {
        gameRef.current.stopGame();
        gameRef.current = null;
      }
      if (inputRef.current) {
        inputRef.current.destroy();
        inputRef.current = null;
      }
    };
  }, [isActive, assetsLoaded, level, timeLimit]); // Removed gameState dependency

  if (assetError) {
    return (
      <div className="game-canvas-error">
        <p>Failed: {assetError}</p>
      </div>
    );
  }

  const getStatusText = () => {
    switch (displayState) {
      case 'loading': return 'Loading...';
      case 'ready': return isActive ? 'Starting...' : 'Waiting...';
      case 'playing': return 'Playing...';
      case 'finished': return 'Complete!';
    }
  };

  return (
    <div className="game-canvas-container">
      <canvas
        ref={canvasRef}
        width={256}
        height={256}
        className="game-canvas"
      />
      <div className="game-status">{getStatusText()}</div>
    </div>
  );
}
