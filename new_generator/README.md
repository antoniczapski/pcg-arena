# Proposal for State-of-the-Art (SOTA) Mario Level Generator

## 1. Analysis of Existing Data and Previous Findings

Our goal is to develop a generator that achieves the highest ELO rating on the PCG Arena platform. To do this, we must ground our design in the empirical data collected during the A/B testing phase.

### Key Insights from EDA (PCG Arena Results)

Based on the analysis of 631 levels, 447 votes, and 14 generators, we have identified the "Golden Features" that correlate with high player preference (Win Rate):

1.  **Playability is King (The "Oatmeal" problem is secondary to "Unplayable"):**
    *   **Finding:** Win Rate is negatively correlated with Death Rate. Players overwhelmingly prefer levels they can actually complete.
    *   **Implication:** The generator *must* guarantee solvability. Hard levels lose. "Original" levels (92.5% Win Rate) have a high completion rate (27.5%) compared to the average (18%).

2.  **Exploration > Linearity:**
    *   **Finding:** The "Flow Channel" hypothesis (people like a specific difficultly band) was *rejected*. Instead, H3 (Path Freedom) was *strongly supported*. Winning levels have **63% higher spatial coverage** (Unique Tiles Visited) and allow for more exploration.
    *   **Implication:** A strict left-to-right linear corridor is boring. The generator should create verticality and multiple paths.

3.  **"Original" is the Benchmark:**
    *   **Finding:** Hand-crafted Nintendo levels dominate (92.5% Win Rate).
    *   **Implication:** Structural mimicry of original levels is a valid strategy. "Pattern-based" generators failed because they captured the *texture* (tiles) but not the *intent* (design patterns like "stairs before jumps").

4.  **MarioGPT is a Strong Baseline:**
    *   **Finding:** `mariogpt` is currently Rank 4 (62.4% Win Rate), performing well among procedural methods.

---

## 2. Top 3 Proposals for SOTA Implementation

We propose three distinct approaches to building the SOTA generator, ranked by estimated potential ELO.

### Proposal 1: RLHF-Tuned MarioGPT (The "Deep Learning SOTA")

**Concept:**
Leverage the "Large Language Model" paradigm but fine-tune it using our specific competitive advantage: **Human Preference Data**.

*   **Base Model:** Use the existing `MarioGPT` (GPT-2 based trained on VGLC).
*   **Technique:** Reinforcement Learning from Human Feedback (RLHF) or Direct Preference Optimization (DPO).
*   **The "Trick":**
    1.  **SFT (Supervised Fine-Tuning):** Fine-tune first on only the "Original" levels and the top 10% rated levels from our DB to shift the distribution towards quality.
    2.  **Reward Modeling:** Train a small Reward Model (RM) to predict the outcome of a battle ($P(Level_A > Level_B)$) using the `battles` and `votes` tables.
    3.  **Optimization:** Use PPO (Proximal Policy Optimization) to update the MarioGPT weights to maximize the score from the Reward Model.
*   **Why it will win:** It directly optimizes the metric we care about (User Preference) using the "SOTA" method currently dominating NLP (ChatGPT-style training).

### Proposal 2: Surrogate-Assisted Evolutionary Search (The "Data-Driven Optimization")

**Concept:**
Instead of a "Black Box" generator, use a Genetic Algorithm (GA) where the fitness function is a Machine Learning model trained on our telemetry.

*   **Representation:** A vector of high-level design parameters (e.g., *enemy_density, gap_width, platform_height_variance*) OR a latent vector from a VAE/GAN.
*   **Surrogate Model (Fitness Function):** Train a **Random Forest Regressor** or **Gradient Boosting Machine** on the 631 levels.
    *   **Input:** Extracted features (Completabilty %, Density, Linearity, Basic Tile Stats).
    *   **Target:** The Glicko-2 Rating of the level.
*   **Process:**
    1.  Generate a population of random level vectors.
    2.  Use the Surrogate Model to predict their Rating.
    3.  Select the best, mutate/crossover.
    4.  **Constraint:** Run an A* agent simulation as a hard constraint. If *Completabilty < 100%*, Fitness = 0.
*   **Why it will win:** It explicitly targets the features we *know* (from EDA) are important. It guarantees solvability (hard constraint) and maximizes predicted fun.

### Proposal 3: Graph-Grammar Level Assembler (The "Robust Engineering" Approach)

**Concept:**
A "Smart Shuffler" that recombines high-quality chunks from "Original" levels using a Graph Grammar or Wave Function Collapse (WFC) with semantic rules.

*   **Chunks:** Extract gameplay-significant chunks from the `original` dataset (e.g., "Pipe Structure", "Staircase", "Enemy Patrol Platform").
*   **Grammar Rules:** Define connectivity rules (e.g., "Pipe must be on Ground", "Gap must be followed by Landing").
*   **Graph Assembly:**
    *   Treat the level as a graph of nodes (Start -> Challenge -> Reward -> End).
    *   Fill nodes with extracted chunks.
    *   Ensure a valid path exists from Start to End using Graph Traversal.
*   **Why it will win:** "Original" levels have a 92% win rate. By re-assembling their atomic parts, we retain the "Nintendo Polish" while creating infinite variation. It solves the "Unplayable" problem by construction (if chunks are valid and connections are valid, the level is valid).

---

## 3. Recommended Implementation Plan

We recommend **Proposal 2 (Surrogate-Assisted Evolution)** as the immediate first step because:
1.  **Fast Iteration:** We already have the data (EDA features) and the "Original" levels.
2.  **Complexity:** It is easier to implement than setting up a full RLHF pipeline for MarioGPT.
3.  **Explainability:** We can inspect the surrogate model to see *why* it thinks a level is good.

**Action Plan:**
1.  **Feature Extraction:** Write a script to convert all `levels` in the DB into feature vectors (using the features analyzed in EDA).
2.  **Model Training:** Train a Regressor (`X=Features`, `y=Glicko`). Verify accuracy (MSE).
3.  **Generator Loop:** Implement a simple GA that optimizes a latent vector or parameter set against this Regressor.
4.  **Validation:** Run the generated levels through the A* agent (using the Java/TypeScript engine integration) to ensure solvability.
