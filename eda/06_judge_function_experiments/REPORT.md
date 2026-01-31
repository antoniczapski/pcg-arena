# Judge Function Experiments - Summary Report
Generated: 2026-01-31 09:22:03.922101

## Experiment Results Summary

### Experiment A: Verticality Validation
- Y-Sigma vs Win Rate: r = 0.263, p = 0.0177
- Path Entropy vs Win Rate: r = 0.331
- Hesitation vs Win Rate: r = -0.091
- Partial Correlation (controlling completion): r = 0.2761217961207105

### Experiment B: Hazard Hierarchy
- Data limitation: gap_density/enemy_density NULL in database
- Pattern generator win rate: 0.268
- Other generator win rate: 0.532

### Experiment C: Death Entropy
- Death Entropy vs Win Rate: r = nan, p = nan
- Early Death Rate vs Win Rate: r = -0.128
- Low entropy win rate: nan
- High entropy win rate: 0.452

### Experiment D: Original Centroid
- Mahalanobis Distance vs Win Rate: r = -0.324, p = 0.0032
- Style Reward vs Win Rate: r = 0.324

## Proposed Judge Function

```
Stage 1 (Static Gatekeeper):
  J_static = w_style * (1/(1+D_M)) - w_gap * GapDensity - w_early * EarlyHazards

Stage 2 (Simulation Judge):
  J_final = J_static + w_vert * σ_y + w_flow * (1-Hesitation) - w_choke * (1-DeathEntropy)
```
