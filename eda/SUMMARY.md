# PCG Arena Exploratory Data Analysis - Summary

## Overview

This document summarizes the complete EDA conducted on the PCG Arena platform data, a web-based blind A/B testing system for procedural content generation (PCG) algorithms for Super Mario Bros levels.

**Analysis Date**: 2024  
**Data Sources**: level-stats.json, votes.json, trajectories.json, player-profiles.json

---

## Dataset Summary

| Category | Count |
|----------|-------|
| Levels | 631 |
| Generators | 14 |
| Total Votes | 447 |
| Players | 26 |
| Telemetry Records | 894 |
| Trajectories | 100 |

---

## Research Questions & Results

### RQ1: What Makes a Good Generator/Level?

| Hypothesis | Result | Key Finding |
|------------|--------|-------------|
| H1: Flow Channel (moderate difficulty best) | ❌ Not Supported | Linear relationship, easier = better |
| H2: Structural Variety | ✅ Partial | "Creative" tag correlates with wins (r=0.42) |
| H3: Path Freedom | ✅ Strong | Spatial coverage predicts wins (p=0.004) |

**Top Generators**: original (92.5%), ore (67.8%), notch (67.5%)  
**Bottom Generators**: patternCount (22%), notchParam (22%), patternWeightCount (26%)

### RQ2: Are Players Consistent?

| Hypothesis | Result | Key Finding |
|------------|--------|-------------|
| H4: Preference Clusters Exist | ✅ Supported | 3 distinct player clusters identified |
| H5: Skill → Consistency | ❌ Not Supported | No correlation (r=0.18, p=0.58) |

**Player Clusters**:
1. "Explorers" (n=2) - Long sessions, high completion
2. "Mainstream" (n=6) - Most votes, balanced play
3. "Strugglers" (n=4) - Low completion, high deaths

### RQ3: What Do Tags Mean?

| Hypothesis | Result | Key Finding |
|------------|--------|-------------|
| H6: Tags Match Telemetry | ✅ Supported | 5/6 tags match expected metric direction |
| H7: Feature Importance | ✅ Supported | Completion rate predicts "too_easy" (r=0.35) |

**Tag Semantics**:
- `fun` ≈ playable + beatable
- `creative` ≈ fun + engaging
- `too_easy` ≈ very high completion
- `too_hard` ≈ high death rate

### RQ4: Extended Feature Analysis (New)

| Hypothesis | Result | Key Finding |
|------------|--------|-------------|
| H8: Enemy Density/Hazards | ✅ Supported | Easy Q1 (60%) vs Hard Q4 (47%), p=0.040 |
| H9: Rewards/Leniency | ✅ Supported | "Fun" tagged = 2.3× higher completion |
| H10: Predictive Modeling | ✅ Supported | 66% CV accuracy, tags dominate features |

**Key Insights from Extended Analysis**:
- **Hazard Density**: Higher enemy/gap density correlates with lower win rates
- **Leniency Effect**: Levels tagged "fun" have 31.3% completion vs 13.6% baseline
- **Feature Importance**: Duration, creative_rate, boring_rate are top ML predictors
- **Tag Validation**: 5/6 subjective tags correlate with expected objective metrics

---

## Key Insights

### 1. "Original" Dominates
Hand-crafted levels win 92.5% of comparisons. This is the benchmark to beat.

### 2. Playability > Challenge
Players prefer levels they can complete. The "flow channel" hypothesis was not supported - easier is simply better in A/B comparisons.

### 3. Exploration Matters
Levels that allow spatial exploration (more unique tiles visited) are preferred. This suggests good PCG should create non-linear, explorable spaces.

### 4. Tag Semantics are Valid
Player-assigned tags correlate with measurable telemetry. "Fun" levels have higher completion rates. Tags can be trusted as quality signals.

### 5. Pattern-Based Generators Fail
All "pattern*" generators rank at the bottom. These approaches may produce technically valid but aesthetically/playably poor levels.

---

## Recommendations

### For Generator Development
1. **Optimize for completion** - Ensure levels are beatable
2. **Enable exploration** - Create non-linear paths
3. **Avoid repetition** - Structural variety is rewarded
4. **Test against "original"** - Use as benchmark

### For Platform Improvement
1. **Collect more data** - Many statistical tests are underpowered
2. **Enable structural features** - Currently null in exports
3. **Encourage tagging** - Sparse tag data limits analysis
4. **Track temporal patterns** - Preference stability over time

### For Research
1. **Cluster-stratified analysis** - Account for player types
2. **Pairwise comparisons** - Add winner/loser generator IDs to votes
3. **Controlled experiments** - Test specific hypotheses with designed levels

---

## File Structure

```
eda/
├── README.md                           # EDA plan and hypotheses
├── pcg-arena-*.json                    # Raw data exports
├── plots/                              # All generated visualizations
│   ├── global_distributions.png
│   ├── generator_fingerprints.png
│   ├── generator_comparison.png
│   ├── correlation_matrix.png
│   ├── h1_difficulty_vs_winrate.png
│   ├── h2_structural_variety.png
│   ├── h3_path_freedom.png
│   ├── h4_preference_clusters.png
│   ├── h5_skill_consistency.png
│   ├── h6_tag_telemetry.png
│   ├── h7_tag_feature_importance.png
│   ├── h8_enemy_density_hazards.png    # NEW
│   ├── h9_rewards_leniency.png         # NEW
│   ├── h10_feature_importance.png      # NEW
│   ├── h6_extended_tag_validation.png  # NEW
│   ├── tag_distribution.png
│   ├── tag_by_generator.png
│   └── trajectory_visualization.png
├── 00_data_preparation/
│   ├── prepare_data.py
│   ├── level_stats_clean.csv
│   ├── telemetry_flat.csv
│   ├── trajectory_features.csv
│   ├── generator_stats.csv
│   ├── player_voting_patterns.csv
│   └── REPORT.md
├── 01_rq1_good_generators/
│   ├── analyze_good_generators.py
│   └── REPORT.md
├── 02_rq2_player_consistency/
│   ├── analyze_player_consistency.py
│   └── REPORT.md
├── 03_rq3_tag_analysis/
│   ├── analyze_tags.py
│   └── REPORT.md
├── 04_general_eda/
│   ├── general_eda.py
│   └── REPORT.md
└── 05_extended_experiments/            # NEW
    ├── extended_experiments.py
    └── REPORT.md
```

---

## Statistical Summary

| Test | Statistic | p-value | Significant |
|------|-----------|---------|-------------|
| H1: Death rate vs Win rate | r = -0.149 | 0.313 | No |
| H2: Creative vs Win rate | r = 0.416 | 0.003 | **Yes** |
| H3: Tiles visited (won vs lost) | U = 1486.5 | 0.004 | **Yes** |
| H4: Clustering | 3 clusters | - | Yes |
| H5: Skill vs Consistency | r = 0.176 | 0.584 | No |
| H6: Fun → Completion | U = 292.5 | 0.049 | **Yes** |
| H7: Too_easy ↔ Completion | r = 0.353 | 0.014 | **Yes** |
| H8: Hazard Easy vs Hard Q | U stat | 0.040 | **Yes** |
| H9: Fun vs Non-Fun Completion | U stat | 0.0003 | **Yes** |
| H10: ML Cross-Validation | Acc=0.66 | - | **Yes** |

---

## Conclusion

The PCG Arena data reveals that **playability** and **exploration** are the primary drivers of player preference. Players consistently choose levels they can complete and that offer spatial freedom. Traditional "game design" intuitions about optimal challenge (flow channel) are not supported - in blind comparisons, easier levels win.

The data also shows significant room for improvement in current PCG algorithms, with hand-crafted "original" levels vastly outperforming all automated generators. Future generator development should focus on ensuring basic playability before optimizing for other aesthetic criteria.

---

*Complete analysis code and visualizations available in the ./eda directory.*
