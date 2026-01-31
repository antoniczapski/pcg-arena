# Mario-DPO: Fun-Tuning Procedural Level Generators

**Title:** *Fun-Tuning: Aligning Procedural Level Generators with Human Playstyle Preferences via Direct Preference Optimization*

## 1. Research Concept (The "Hook")

Most Procedural Content Generation (PCG) methods optimize for **validity** (is it playable?) or **diversity** (is it unique?). This project proposes the first framework optimized for **Human Preference** (is it fun?) using **Direct Preference Optimization (DPO)**.

We address the "Small Data" problem inherent in PCG human feedback by using a neuro-symbolic **Judge Function** (derived from our PCG Arena experiments) to bootstrap a large synthetic dataset via **RLAIF (Reinforcement Learning from AI Feedback)**.

**Core Innovation:** Moving from "Generating Levels" to "Aligning Generative Models with Human Intent."

---

## 2. Architecture

We will not build a GAN or a standard Genetic Algorithm. We will build a **Language Model for Levels**.

### Phase 1: The Backbone (MarioGPT-2)
*   **Model:** A standard Transformer decoder (GPT-2 architecture).
*   **Data Source:** Use the existing "Original" Super Mario Bros levels found in `db/seed/levels/original` (and potentially `shared/level-format`) as the training corpus.
*   **Objective:** Train on the "grammar" of Mario levels (pipes go on ground, blocks float, etc.).
*   **Outcome:** A base model that generates *valid* but *generic* levels ($ \pi_{ref} $).

### Phase 2: Data Expansion (Constitutional AI / RLAIF)
Since our 447 human votes are valuable but insufficient for deep learning (~10k+ pairs needed), we will use **RLAIF**:
1.  **Generate:** Create ~20,000 random level pairs using the Phase 1 Base Model.
2.  **Judge:** Run the **Simulation Agent (A*)** on these levels to extract dynamic features.
3.  **Score:** Apply the **Judge Function ($J_{final}$)** derived from our research findings:
    *   **Reward:** Verticality ($\sigma_y$, Exp A) + Style Similarity ($D_M$, Exp D).
    *   **Penalize:** Chokepoints (Death Entropy, Exp C) + Gap Spam (Exp B).
    $$ J_{final} = w_{style}\frac{1}{1+D_M} - w_{gap}\text{Gap} + w_{vert}\sigma_y + w_{flow}(1-\text{Hes}) $$
4.  **Label:** Create a "Synthetic Preference Dataset" where `Winner = HighScore` and `Loser = LowScore`.
5.  **Mix:** Combine with the 447 *real* human votes (weighted 10x higher) to ground the synthetic data in reality.

### Phase 3: The Alignment (DPO)
*   **Method:** **Direct Preference Optimization (DPO)**.
*   **Mechanism:** Fine-tune the Transformer on the pairs $(x, y_{win}, y_{loss})$ to maximize the likelihood of the winner while suppressing the loser, relative to the reference model.
*   **Result:** The model *implicitly* learns research findings (e.g., "flat levels with gaps = bad", "vertical flow = good") without hard-coded rules.

---

## 3. Implementation Details for SOTA Performance

### A. Inference-Time Rejection Sampling ("The Safety Net")
Data analysis showed `patternCount` had a 2.3% completion rate. We must ensure playability.
*   **Technique:** Generate batch $N=10$.
*   **Filter:** Run fast A* agent. Discard unplayable levels.
*   **Select:** From the remaining, pick the one with the highest **Judge Score ($J_{final}$)**.

### B. Style Conditioning ("The Nintendo Factor")
Experiment D showed high-quality levels cluster near the "Original" centroid.
*   **Technique:** Prepend control tokens to the prompt, e.g., `[STYLE: NINTENDO]` or `[STYLE: CHAOS]`.
*   **Training:** During DPO, associate high-verticality/high-flow levels with the `[STYLE: NINTENDO]` token. This gives control over the generated "vibe".

---

## 4. Evaluation Strategy ("The Killer Graph")

To target NeurIPS/ICLR/CoG, we need to demonstrate statistical parity with human content.

**The Target Graph:**
*   **X-Axis:** Training Steps / Data Scale.
*   **Y-Axis:** Win Rate in PCG Arena (vs "Original").
*   **Baselines:** MarioGPT (Base), GAN, Constructive.
*   **Success Metric:** Mario-DPO starts low, climbs, and crosses the 50% win rate threshold against Original levels.

**Claim:** *"Our aligned model is the first procedural generator to achieve statistical parity with human-authored content in blind A/B testing."*

---

## 5. Project Roadmap

### Step 1: Data Preparation
- [ ] Aggregate "Original" levels from `db/seed/levels/original` into a text corpus.
- [ ] Tokenize level data (mapping tiles to characters).
- [ ] Prepare the `votes.json` and `trajectories.json` for the validation set.

### Step 2: Base Model Training (SFT)
- [ ] Implement GPT-2 Architecture (PyTorch/HuggingFace).
- [ ] Train on the level corpus.
- [ ] Evaluate validity (A* solvability rate) of base model.

### Step 3: Judge Function & Synthetic Data
- [ ] Implement the automated Judge Function $J_{final}$ in Python (using weights from `eda/06_judge_function_experiments`).
- [ ] Generate 20k pairs from Base Model.
- [ ] Run A* simulation and feature extraction on all 20k pairs.
- [ ] Auto-label pairs based on $J_{final}$ score.
- [ ] Mix with human preference data (PCG Arena exports).

### Step 4: DPO Fine-Tuning
- [ ] Implement DPO Loss function.
- [ ] Fine-tune the Base Model on the preference dataset.
- [ ] Monitor validation loss on human-held-out set.

### Step 5: Integration & Evaluation
- [ ] Export model to `generators/MarioDPO`.
- [ ] Implement the Rejection Sampling wrapper.
- [ ] Deploy to PCG Arena local instance.
- [ ] Run evaluations against "Original" levels.

---

## Reference: The Derived Judge Function
(From `eda/06_judge_function_experiments`)

```python
def calculate_fitness(level, trajectory):
    # Stage 1: Static
    style_dist = mahalanobis_distance(level, original_centroid)
    j_static = w_style * (1/(1+style_dist)) - w_gap * level.gap_density - w_early * level.early_hazards
    
    # Stage 2: Dynamic (if playable)
    if not trajectory.complete:
        return score_min
        
    y_sigma = std(trajectory.y_coords) # Verticality
    hesitation = count(vel_x approx 0) / len(trajectory) # Flow
    death_ent = entropy(trajectory.death_locs) # Fairness
    
    j_final = j_static + w_vert * y_sigma + w_flow * (1 - hesitation) + w_choke * death_ent
    return j_final
```
