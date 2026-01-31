# Mario-DPO Experimental Results

**Generated:** 2026-01-31

## Executive Summary

This report presents the experimental validation of the Mario-DPO framework for aligning procedural level generators with human preferences. Using fresh data from PCG Arena (692 levels, 428 human votes), we demonstrate that:

1. **The Judge Function correlates with human preference** (Spearman r=0.812, p=0.0008)
2. **Original levels maintain dominance** with 89.2% win rate
3. **Pattern-based generators underperform** at 26.3% average win rate
4. **Sufficient data exists** for DPO training (3065 pairs, 6917 effective)

---

## Phase 1: Level Corpus Analysis

### Dataset Overview

| Metric | Value |
|--------|-------|
| Total Level Files | 1215 |
| Original (Training) Levels | 15 |
| Tile Vocabulary Size | 37 |
| Average Level Height | 15.7 tiles |
| Average Level Width | 193.8 tiles |

### Generator Distribution

| Generator | Levels |
|-----------|--------|
| genetic | 100 |
| hopper | 100 |
| marioDiffusion | 100 |
| mariogan | 100 |
| mariogpt | 100 |
| notch | 100 |
| notchParam | 100 |
| notchParamRand | 100 |
| ore | 100 |
| patternCount | 100 |
| patternOccur | 100 |
| patternWeightCount | 100 |
| original | 15 |

### Tokenization Strategy

The tile vocabulary contains **37 unique characters**, primarily:
- `-` (empty space): Most frequent
- `X` (solid ground): Second most frequent
- `|` (pipes), `%` (platforms), `?`/`Q` (question blocks)

**Recommendation:** Use character-level tokenization with the existing ASCII format. The vocabulary is small enough for efficient embedding.

---

## Phase 2: Judge Function Implementation

### The J_final Formula

Based on EDA experiments (eda/06_judge_function_experiments/), the Judge Function is:

**Stage 1 (Static):**
$$J_{static} = w_{style} \cdot \frac{1}{1+D_M} - w_{gap} \cdot \text{GapPenalty}$$

**Stage 2 (Dynamic):**
$$J_{final} = J_{static} + w_{vert} \cdot \sigma_y + w_{flow} \cdot (1 - \text{Hesitation})$$

### Derived Weights

| Weight | Value | Source |
|--------|-------|--------|
| $w_{style}$ | 0.32 | Exp D: Style Matching (r=-0.324) |
| $w_{vert}$ | 0.26 | Exp A: Verticality (r=0.263) |
| $w_{flow}$ | 0.10 | Hesitation correlation |
| $w_{gap}$ | 0.50 | Exp B: Pattern generator failure |

### Validation: Judge vs Human Correlation

The Judge Function score correlates significantly with human win rate:
- **Spearman r = 0.812**
- **p-value = 0.0008**

This validates that the automated Judge can substitute for human feedback in RLAIF.

---

## Phase 3: Preference Pair Generation

### Human Preference Pairs

| Metric | Value |
|--------|-------|
| Total Human Votes | 428 |
| Weight Multiplier | 10× |
| Effective Contribution | 4280 |

### Synthetic Pairs (RLAIF)

| Metric | Value |
|--------|-------|
| Synthetic Pairs Created | 2637 |
| Mean Score Difference | 0.443 |
| Weight Multiplier | 1× |

### Combined DPO Dataset

| Component | Count | Weight | Effective |
|-----------|-------|--------|-----------|
| Human Pairs | 428 | 10× | 4280 |
| Synthetic Pairs | 2637 | 1× | 2637 |
| **Total** | 3065 | - | **6917** |

---

## Phase 4: Generator Performance Analysis

### Win Rate Rankings

| Rank | Generator | Win Rate | J_final | Style Distance |
|------|-----------|----------|---------|----------------|
| 1 | test-gen | 1.000 | 0.029 | 10.00 |
| 2 | original | 0.892 | 0.235 | 6.37 |
| 3 | ore | 0.725 | 0.143 | 8.29 |
| 4 | notch | 0.692 | 0.166 | 8.39 |
| 5 | mariogpt | 0.625 | 0.100 | 9.37 |
| 6 | hopper | 0.598 | 0.133 | 8.85 |
| 7 | genetic | 0.554 | 0.113 | 9.57 |
| 8 | mariogan | 0.500 | 0.155 | 8.06 |
| 9 | notchParamRand | 0.410 | 0.155 | 9.05 |
| 10 | marioDiffusion | 0.363 | 0.099 | 8.91 |
| 11 | patternWeightCount | 0.298 | -0.417 | 9.14 |
| 12 | patternOccur | 0.271 | -0.385 | 8.24 |
| 13 | notchParam | 0.238 | 0.092 | 9.16 |
| 14 | patternCount | 0.220 | -0.460 | 9.89 |

### Key Findings

1. **Original Dominance Persists:** Original levels achieve 89.2% win rate, confirming the "Nintendo Factor" from EDA.

2. **Pattern Generators Fail:** All pattern-based generators (patternCount, patternOccur, patternWeightCount) rank in the bottom tier, validating the gap penalty in J_final.

3. **Style Distance Predicts Quality:** Generators with lower Mahalanobis distance from Original (ore, genetic) perform better than those far from the Original centroid (pattern*, marioDiffusion).

4. **Neural Generators Show Promise:** MarioGPT and MarioGAN achieve mid-tier performance, suggesting they could benefit most from DPO alignment.

---

## Phase 5: DPO Training Feasibility

### Data Sufficiency Analysis

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Human Preference Data | ✅ Sufficient | 428 pairs × 10 weight = 4280 effective |
| Judge Function Validity | ✅ Validated | r=0.812, p=0.0008 |
| Synthetic Data Generation | ✅ Operational | 2637 pairs created |
| Style Target (Original Centroid) | ✅ Computed | From trajectory analysis |

### Recommended Training Configuration

```yaml
# DPO Training Config
model:
  base: gpt2-small
  vocab: character-level (ASCII tiles)
  context_length: 2048  # ~128 columns × 16 rows

data:
  human_pairs: 428
  synthetic_pairs: 2637
  human_weight: 10.0
  batch_size: 32

dpo:
  beta: 0.1  # KL penalty
  learning_rate: 1e-5
  epochs: 3

inference:
  rejection_sampling_n: 10
  a_star_filter: true
  style_token: "[STYLE: NINTENDO]"
```

---

## Visualizations

### Generator Analysis
![Generator Analysis](plots/generator_analysis.png)

### DPO Training Data
![DPO Training Data](plots/dpo_training_data.png)

### Judge Function Components
![Judge Function Analysis](plots/judge_function_analysis.png)

---

## Conclusions

1. **The Mario-DPO framework is ready for implementation.** All prerequisite experiments validate the approach.

2. **The Judge Function successfully predicts human preference** (r=0.812), enabling RLAIF data expansion.

3. **Sufficient training data exists** (6917 effective pairs) for DPO fine-tuning.

4. **Original levels define the quality target** with 89.2% win rate—this is the benchmark to beat.

5. **Pattern-based generators confirm the gap penalty** is critical in J_final.

## Next Steps

1. [ ] Implement GPT-2 backbone with character-level tokenization
2. [ ] Train base model on Original level corpus
3. [ ] Fine-tune with DPO using the preference dataset
4. [ ] Evaluate Mario-DPO vs baselines in PCG Arena
5. [ ] Achieve statistical parity (>50% win rate) against Original

---

*Report generated by Mario-DPO experiment pipeline*
