/**
 * Stage 5: Level Detail Page
 * 
 * Shows detailed statistics and death heatmap overlaid on level preview.
 */

import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArenaApiClient } from '../api/client';
import { assetLoader } from '../engine/graphics/AssetLoader';
import { MarioLevel } from '../engine/MarioLevel';
import { SpriteType } from '../engine/SpriteType';
import type { LevelStatsResponse, LevelHeatmapResponse, LevelPreviewData } from '../api/types';
import './LevelDetailPage.css';

// Create singleton API client
const apiClient = new ArenaApiClient(import.meta.env.VITE_API_BASE_URL || '');

const TILE_SIZE = 16;
const SKY_COLOR = '#5c94fc';

export function LevelDetailPage() {
  const { levelId } = useParams<{ levelId: string }>();
  const [stats, setStats] = useState<LevelStatsResponse | null>(null);
  const [heatmap, setHeatmap] = useState<LevelHeatmapResponse | null>(null);
  const [levelData, setLevelData] = useState<LevelPreviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [assetsLoaded, setAssetsLoaded] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayRef = useRef<HTMLCanvasElement>(null);

  // Load assets on mount
  useEffect(() => {
    assetLoader.loadAllAssets()
      .then(() => setAssetsLoaded(true))
      .catch(err => console.error('Failed to load assets:', err));
  }, []);

  // Fetch level data
  useEffect(() => {
    if (!levelId) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        const [statsRes, heatmapRes] = await Promise.all([
          apiClient.getLevelStats(levelId),
          apiClient.getLevelHeatmap(levelId)
        ]);
        setStats(statsRes);
        setHeatmap(heatmapRes);
        
        // Fetch the level tilemap from generator details
        if (statsRes.stats.generator_id) {
          try {
            const genResponse = await apiClient.getGenerator(statsRes.stats.generator_id);
            const level = genResponse.levels.find(l => l.level_id === levelId);
            if (level) {
              setLevelData(level);
            }
          } catch (genErr) {
            console.error('Failed to fetch level tilemap:', genErr);
          }
        }
        
        setError(null);
      } catch (err) {
        console.error('Failed to fetch level data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load level data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [levelId]);

  // Render level and heatmap overlay
  useEffect(() => {
    if (!assetsLoaded || !levelData || !canvasRef.current || !overlayRef.current) return;

    const canvas = canvasRef.current;
    const overlay = overlayRef.current;
    const ctx = canvas.getContext('2d');
    const overlayCtx = overlay.getContext('2d');
    if (!ctx || !overlayCtx) return;

    // Parse level
    const level = new MarioLevel(levelData.tilemap, true);
    const tileWidth = level.tileWidth;
    const tileHeight = level.tileHeight;

    // Set canvas dimensions
    canvas.width = tileWidth * TILE_SIZE;
    canvas.height = tileHeight * TILE_SIZE;
    overlay.width = tileWidth * TILE_SIZE;
    overlay.height = tileHeight * TILE_SIZE;

    // Draw level background
    ctx.fillStyle = SKY_COLOR;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw tiles
    for (let tileY = 0; tileY < tileHeight; tileY++) {
      for (let tileX = 0; tileX < tileWidth; tileX++) {
        const tileIndex = level.getBlock(tileX, tileY);
        if (tileIndex !== 0) {
          assetLoader.drawTile(ctx, tileIndex, tileX * TILE_SIZE, tileY * TILE_SIZE);
        }
      }
    }

    // Draw enemies
    for (let tileY = 0; tileY < tileHeight; tileY++) {
      for (let tileX = 0; tileX < tileWidth; tileX++) {
        const spriteType = level.getSpriteType(tileX, tileY);
        if (spriteType !== SpriteType.NONE) {
          drawEnemy(ctx, spriteType, tileX, tileY);
        }
      }
    }

    // Clear overlay
    overlayCtx.clearRect(0, 0, overlay.width, overlay.height);

    // Draw death heatmap overlay
    if (heatmap && heatmap.death_heatmap.data.length > 0) {
      const maxCount = heatmap.death_heatmap.max_count || 1;
      
      for (const point of heatmap.death_heatmap.data) {
        const intensity = point.count / maxCount;
        const alpha = 0.2 + (0.5 * intensity);
        
        // Draw gradient column for death location
        const gradient = overlayCtx.createLinearGradient(
          point.tile_x * TILE_SIZE, 0,
          point.tile_x * TILE_SIZE, overlay.height
        );
        gradient.addColorStop(0, `rgba(255, 0, 0, ${alpha * 0.3})`);
        gradient.addColorStop(0.5, `rgba(255, 0, 0, ${alpha})`);
        gradient.addColorStop(1, `rgba(255, 0, 0, ${alpha * 0.5})`);
        
        overlayCtx.fillStyle = gradient;
        overlayCtx.fillRect(point.tile_x * TILE_SIZE, 0, TILE_SIZE, overlay.height);
      }
    }

    // Add heatmap legend on overlay
    if (heatmap) {
      overlayCtx.fillStyle = 'rgba(0, 0, 0, 0.7)';
      overlayCtx.fillRect(5, overlay.height - 22, 180, 18);
      overlayCtx.fillStyle = '#fff';
      overlayCtx.font = 'bold 11px sans-serif';
      overlayCtx.fillText(
        `☠ Deaths: ${heatmap.death_heatmap.total_deaths} | Samples: ${heatmap.sample_count}`,
        10,
        overlay.height - 8
      );
    }

  }, [assetsLoaded, levelData, heatmap]);

  function drawEnemy(ctx: CanvasRenderingContext2D, spriteType: SpriteType, tileX: number, tileY: number) {
    let frameY = 0;
    const ENEMY_SPRITE_HEIGHT = 32;

    switch (spriteType) {
      case SpriteType.RED_KOOPA:
      case SpriteType.RED_KOOPA_WINGED:
        frameY = 0;
        break;
      case SpriteType.GREEN_KOOPA:
      case SpriteType.GREEN_KOOPA_WINGED:
        frameY = 1;
        break;
      case SpriteType.GOOMBA:
      case SpriteType.GOOMBA_WINGED:
        frameY = 2;
        break;
      case SpriteType.SPIKY:
      case SpriteType.SPIKY_WINGED:
        frameY = 3;
        break;
      case SpriteType.BULLET_BILL:
        frameY = 5;
        break;
      case SpriteType.ENEMY_FLOWER:
        const flowerX = tileX * TILE_SIZE + 9;
        const flowerY = tileY * TILE_SIZE - 8;
        assetLoader.drawSprite(ctx, 'enemies', 0, 6, flowerX, flowerY);
        return;
      default:
        return;
    }

    const x = tileX * TILE_SIZE;
    const y = (tileY + 1) * TILE_SIZE - ENEMY_SPRITE_HEIGHT;
    assetLoader.drawSprite(ctx, 'enemies', 0, frameY, x, y);
  }

  if (loading) {
    return (
      <div className="level-detail-page">
        <div className="level-loading">Loading level data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="level-detail-page">
        <div className="level-error">{error}</div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="level-detail-page">
        <div className="level-error">Level not found</div>
      </div>
    );
  }

  const { performance, outcomes, tags, difficulty } = stats.stats;
  const features = stats.features;

  return (
    <div className="level-detail-page">
      <div className="level-header">
        <Link to={`/generator/${stats.stats.generator_id}`} className="back-link">
          ← Back to Generator
        </Link>
        <h1>Level Statistics</h1>
        <p className="level-id">{stats.level_id}</p>
      </div>

      <div className="level-grid">
        {/* Performance Card */}
        <div className="level-card performance-card">
          <h2>Performance</h2>
          <div className="metrics-grid">
            <div className="metric">
              <span className="value">{performance.times_shown || 0}</span>
              <span className="label">Times Shown</span>
            </div>
            <div className="metric">
              <span className="value">
                {performance.win_rate !== undefined 
                  ? `${(performance.win_rate * 100).toFixed(1)}%` 
                  : 'N/A'}
              </span>
              <span className="label">Win Rate</span>
            </div>
            <div className="metric">
              <span className="value">
                {performance.completion_rate !== undefined 
                  ? `${(performance.completion_rate * 100).toFixed(1)}%` 
                  : 'N/A'}
              </span>
              <span className="label">Completion Rate</span>
            </div>
            <div className="metric">
              <span className="value">
                {performance.avg_deaths !== undefined 
                  ? performance.avg_deaths.toFixed(1) 
                  : 'N/A'}
              </span>
              <span className="label">Avg Deaths</span>
            </div>
          </div>
        </div>

        {/* Difficulty Card */}
        <div className="level-card difficulty-card">
          <h2>Difficulty</h2>
          <div className="difficulty-display">
            <span className={`difficulty-badge ${difficulty.classification}`}>
              {difficulty.classification?.replace('_', ' ').toUpperCase() || 'UNKNOWN'}
            </span>
            {difficulty.score !== undefined && (
              <div className="difficulty-bar">
                <div 
                  className="difficulty-fill"
                  style={{ width: `${difficulty.score * 100}%` }}
                />
              </div>
            )}
          </div>
        </div>

        {/* Battle Outcomes */}
        <div className="level-card outcomes-card">
          <h2>Battle Outcomes</h2>
          <div className="outcomes-grid">
            <div className="outcome win">
              <span className="count">{outcomes.wins || 0}</span>
              <span className="label">Wins</span>
            </div>
            <div className="outcome loss">
              <span className="count">{outcomes.losses || 0}</span>
              <span className="label">Losses</span>
            </div>
            <div className="outcome tie">
              <span className="count">{outcomes.ties || 0}</span>
              <span className="label">Ties</span>
            </div>
            <div className="outcome skip">
              <span className="count">{outcomes.skips || 0}</span>
              <span className="label">Skips</span>
            </div>
          </div>
        </div>

        {/* Tags Card */}
        <div className="level-card tags-card">
          <h2>Player Tags</h2>
          <div className="tags-list">
            {Object.entries(tags || {}).map(([tag, count]) => (
              count > 0 && (
                <div key={tag} className="tag-item">
                  <span className="tag-name">{tag.replace('_', ' ')}</span>
                  <span className="tag-count">{count}</span>
                </div>
              )
            ))}
            {Object.values(tags || {}).every(v => v === 0) && (
              <p className="no-tags">No tags yet</p>
            )}
          </div>
        </div>

        {/* Death Heatmap */}
        <div className="level-card heatmap-card full-width">
          <h2>Death Heatmap</h2>
          <p className="heatmap-description">
            Red overlay shows where players died most frequently. Brighter red = more deaths.
          </p>
          <div className="heatmap-container">
            <div className="heatmap-layers">
              <canvas ref={canvasRef} className="heatmap-level-canvas" />
              <canvas ref={overlayRef} className="heatmap-overlay-canvas" />
            </div>
          </div>
          {!levelData && !loading && (
            <p className="no-data">Level preview not available</p>
          )}
          {heatmap && heatmap.sample_count === 0 && levelData && (
            <p className="no-data">No death data yet - play some games!</p>
          )}
        </div>

        {/* Features Card */}
        {features && (
          <div className="level-card features-card">
            <h2>Level Features</h2>
            <div className="features-grid">
              <div className="feature-group">
                <h3>Dimensions</h3>
                <p>{features.dimensions.width} × {features.dimensions.height}</p>
              </div>
              <div className="feature-group">
                <h3>Enemies</h3>
                <p>{features.enemies.total} total</p>
                <small>Density: {features.metrics.enemy_density?.toFixed(3)}</small>
              </div>
              <div className="feature-group">
                <h3>Coins</h3>
                <p>{features.tiles.coin}</p>
                <small>Density: {features.metrics.coin_density?.toFixed(3)}</small>
              </div>
              <div className="feature-group">
                <h3>Gaps</h3>
                <p>{features.structure.gap_count} gaps</p>
                <small>Max width: {features.structure.max_gap_width}</small>
              </div>
              <div className="feature-group">
                <h3>Complexity</h3>
                <p>{((features.metrics.structural_complexity || 0) * 100).toFixed(0)}%</p>
              </div>
              <div className="feature-group">
                <h3>Leniency</h3>
                <p>{((features.metrics.leniency_score || 0) * 100).toFixed(0)}%</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

