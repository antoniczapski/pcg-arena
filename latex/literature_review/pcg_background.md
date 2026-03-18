# PCG Background for Masters Thesis

> **Purpose:** This document synthesises all PCG-related background material for the masters thesis *"PCG Arena: A Platform for Blind A/B Testing of Procedural Content Generators with Direct Preference Optimization."* It is structured to map directly onto the thesis outline (Chapter 2). Material on arena/ranking systems, RLHF/DPO, and individual seed generators is deferred to separate companion documents.

---

## 1. Procedural Content Generation — Definitions and Taxonomy

Procedural Content Generation (PCG) refers to the algorithmic creation of game content with limited or indirect human input (Togelius et al., 2011; Summerville et al., 2018). Content spans levels, maps, rules, characters, weapons, narratives, textures, and sound. PCG has a long commercial history — *Rogue* (1980) and *Elite* (1984) used algorithmic generation to overcome memory constraints — but only in the 2000s–2010s did the academic community begin systematically formalising, benchmarking, and evaluating these techniques.

### 1.1 Generation Paradigms

The PCG literature organises generators along several axes. The most common taxonomy (Togelius et al., 2011; Summerville et al., 2018) distinguishes:

| Paradigm | Core idea | Strengths | Limitations |
|---|---|---|---|
| **Constructive / Rule-based** | Sequentially place content according to hand-authored rules or grammars | Fast; guarantees constraints; interpretable | Limited expressiveness; designer effort |
| **Search-based (SBPCG)** | Frame generation as optimisation over a fitness function, typically with evolutionary algorithms | Flexible objectives; designer control via fitness | Slow (many evaluations); fitness design is non-trivial |
| **Grammar / Pattern-based** | Use formal grammars, design patterns, or n-grams to encode structure | Captures human idioms; supports rhythm and style | Requires pattern libraries; may over-imitate |
| **Machine-learning (PCGML)** | Train neural networks on existing human-designed content to learn implicit design knowledge | Data-driven; can capture complex distributions | Requires training data; may lack diversity; playability not guaranteed |
| **RL-based (PCGRL)** | Frame level design as a Markov Decision Process; train an RL agent to construct levels | No training corpus needed; online generation; optimises for quality criteria | Reward design is hard; training cost; diversity requires special mechanisms |

These paradigms are not mutually exclusive. Many modern systems are **hybrid**: MarioGAN (Volz et al., 2018) combines a learned GAN with CMA-ES search; Nam et al. (2024) pair RL with conditional GANs; Shi & Chen (2016) blend hand-crafted rules with a learned quality classifier.

### 1.2 Online vs. Offline Generation

A further axis distinguishes **offline** generation (content is pre-computed before the game ships) from **online** generation (content is created at runtime, potentially adapting to the player). Online generation imposes stricter time budgets and reliability constraints but enables personalisation — a theme central to experience-driven PCG (Yannakakis & Togelius, 2011).

### 1.3 Controllability

A desirable property of any generator is **controllability**: the ability to accept parameters describing desired content features and produce content that complies. The 2010 Mario AI Level Generation Competition (Shaker et al., 2011) explicitly required generators to adapt to player behaviour metrics, making controllability a first-class evaluation criterion.

---

## 2. Super Mario Bros as a PCG Benchmark

### 2.1 Why Super Mario Bros?

Super Mario Bros (SMB) has become the *de facto* benchmark for PCG research for several reasons:

- **Rich yet tractable design space.** Levels are 2D tile grids with a fixed vocabulary (~10–30 tile types) yet support diverse gameplay through spatial arrangement of platforms, gaps, enemies, pipes, and power-ups.
- **Well-understood physics and mechanics.** The game introduces no new mechanics after the first level; variety comes purely from level design, isolating the variable of interest.
- **Existing AI infrastructure.** The Mario AI Framework (Karakovskiy & Togelius, 2012) provides a standardised Java environment with pluggable controllers (A\* agents, RL agents) and level interfaces, enabling reproducible evaluation across studies.
- **Cultural familiarity.** Nearly all experimental subjects understand the game's controls and goals, reducing training overhead in human studies.

### 2.2 The Mario AI Framework and Competition

The Mario AI Framework is an open-source Java implementation based on *Infinite Mario Bros* (Markus Persson, 2008), a public-domain clone of Nintendo's Super Mario Bros. It served as the basis for three tracks of the Mario AI Championship (2009–2012):

1. **Gameplay Track** — build a controller that plays levels as well as possible.
2. **Learning Track** — build a controller that learns to play.
3. **Level Generation Track** — build software that generates levels for human players.

The Level Generation Track (Shaker et al., 2011) was the world's first academic PCG competition. Generators received gameplay metrics from a "test level" and had 60 seconds to produce a personalised level. Six entries competed; evaluation used **pairwise forced-choice** ("which was more fun?") with 15 human judges. This competition established several norms that influenced later research:

- Pairwise comparison as the preferred human evaluation protocol.
- Player telemetry (jumps, kills, deaths, coins, time) as input to adaptive generators.
- The A\* agent (Robin Baumgarten, 2009 champion) as a de facto playability oracle.

### 2.3 Level Representations

SMB levels are stored as 2D character grids (the ASCII tilemap format), where each character encodes a functional tile type. The Video Game Level Corpus (VGLC; Summerville et al., 2016) standardised this encoding across all 32 original SMB levels and has been used as training data by GANs, LSTMs, Markov Chains, and constraint-based generators.

A key design decision when using neural sequence models is **tokenisation order**:
- **Row-major** (left-to-right, top-to-bottom) is the default for image-like data but separates vertically adjacent tiles (e.g., pipe segments) by the full level width.
- **Column-major / "snaking"** (column-by-column, alternating up/down) keeps vertical neighbours adjacent, preserving local structural dependencies. Summerville & Mateas (2016) showed that this formulation yields the best LSTM generation quality, and PCG Arena's MarioDPO generator adopts column-major tokenisation for the same reason.

---

## 3. Generation Methods Applied to Super Mario Bros

This section surveys the major classes of Mario level generators, ordered roughly by paradigm and chronology. Each subsection is kept brief; deeper coverage of generators used in PCG Arena is deferred to a dedicated thesis section.

### 3.1 Constructive and Rule-Based Generators

The **Notch generator** ships with Infinite Mario Bros. It constructs levels incrementally, placing chunks (platforms, gaps, enemies) according to difficulty-parameterised heuristics. While fast and reliable, its expressive range is narrow and its outputs lack deliberate structure (Shaker et al., 2012).

**Launchpad** (Smith & Whitehead, 2010) generates rhythm-based 2D platformer levels by assigning player actions to beats and mapping them to geometry via a design grammar. A pool of candidate levels is filtered by critics (line-distance, component-distance). Launchpad's publication introduced **Expressive Range Analysis** (ERA) — the dominant characterisation method for PCG generators (Section 4.2).

**Occupancy-Regulated Extension (ORE)** (Mawhorter & Mateas, 2010) generates levels by iteratively extending partial designs according to occupancy rules, producing structurally distinctive levels that score very differently from Notch-style generators on standard metrics.

### 3.2 Search-Based Generators

Search-based PCG frames generation as optimisation. Typical choices include:

- **Genetic algorithms** evolving tile grids or parameter vectors against fitness functions incorporating playability, difficulty targets, and aesthetic criteria.
- **CMA-ES** searching the latent space of a trained generative model (Volz et al., 2018) — effectively a hybrid approach.

The **Mario AI Level Generation Competition** entries (Shaker et al., 2011) represent early search-based generators, including Weber's ProMP (multi-pass constructive with implicit search) and Sorenson's rhythm-based evolutionary generator.

### 3.3 Grammar and Pattern-Based Generators

**Grammatical Evolution (GE)** (Shaker et al., 2012) uses a context-free grammar to encode design rules for Mario levels. GE maps integer genotypes to phenotypes (chunk placements) via production rules, enabling compact representations and interpretable outputs. Conflicts (overlapping chunks) are resolved via priority rules. The paper extends ERA with new aesthetic measures (linearity, leniency, density, NCD) for cross-generator comparison.

**Pattern-based generation** (Dahlskog & Togelius, 2014) represents levels as sequences of vertical micro-patterns (slices) extracted from original SMB levels and searches for meso-patterns (multi-slice structures like enemy hordes, gaps, valleys, stairs) using evolutionary algorithms. This approach explicitly bridges human design idioms and algorithmic search.

### 3.4 Machine-Learning Generators (PCGML)

**LSTM-based generation** (Summerville & Mateas, 2016; Summerville et al., 2016) treats level columns as a sequence and trains a 3-layer, 512-unit LSTM to predict the next tile given history. Key innovations include the *snaking-path-depth* data formulation and co-generation of levels with player paths (from A\* agents or human video traces), achieving 97% playability — higher than any rule-based system at the time.

**MarioGAN** (Volz et al., 2018) trains a Deep Convolutional GAN (DCGAN, Wasserstein variant) on sliding-window segments from a single original SMB level. The trained generator maps 32-dimensional latent vectors to 28×14 tile grids. CMA-ES then searches the latent space to optimise fitness functions based on tile distributions or agent-derived playability/difficulty. This work established the **Latent Variable Evolution (LVE)** paradigm for PCGML.

**MarioGPT** (Sudhakaran et al., 2023) fine-tunes GPT-2 on the VGLC corpus with text prompts controlling high-level features ("many pipes", "no enemies"), enabling natural-language-controllable generation.

**Conditional GAN (CGAN)** (Nam et al., 2024) conditions generation on adjacent patterns to ensure natural connectivity, used within an RL-based pipeline (Section 3.5).

### 3.5 Reinforcement-Learning Generators (PCGRL)

**PCGRL** (Khalifa et al., 2020) formalises level design as an MDP with three representation schemes (Narrow, Turtle, Wide) and trains RL agents to edit tile grids. Change Percentage determines episode termination.

**Nam et al. (2024)** extend PCGRL to Super Mario Bros with several innovations:
- **Human-like AI agents** that model input timing inaccuracies for difficulty assessment.
- **Virtual Simulation (VS)** assigning intermediate rewards via Monte Carlo rollouts to address the credit assignment problem.
- **Diversity-Aware Greedy Policy (DAGP)** selecting actions that are "not bad but distant" from the greedy choice, measured by KL-divergence over tile arrangements.
- A human study (n = 33) validates that generated levels exhibit natural connectivity, appropriate difficulty, non-monotony, and diversity.

---

## 4. Evaluation Methods for Procedurally Generated Content

Evaluation is the central methodological challenge in PCG research — and the primary motivation for PCG Arena. This section surveys the four families of evaluation methods and their evolution over 15+ years, then presents a consolidated comparison table.

### 4.1 Automated Structural Metrics

The earliest and most widely used metrics are **static** — computed directly from the tile grid without simulating gameplay.

**Linearity** measures vertical profile variation. Smith & Whitehead (2010) define it via linear regression on platform midpoints: $\text{Linearity} = \frac{1}{N}\sum |y_i - \hat{y}_i|$, normalised to [0, 1] where 0 = highly linear. Later works (Horn et al., 2014; Summerville et al., 2017) use $R^2$ goodness-of-fit instead, inverting the scale. These incompatible definitions complicate cross-paper comparisons.

**Leniency** approximates difficulty through weighted sums of game objects. At least three incompatible formulations exist:
1. *Smith & Whitehead (2010):* component scores (+1 for gaps/enemies, −1 for safe jumps), normalised.
2. *Shaker et al. (2012):* chunk-weighted sum (gaps, enemies, cannons, tubes, power-ups).
3. *Marino/Summerville:* power-ups +1, cannons/tubes/gaps −0.5, enemies −1, minus average gap width.

Critically, Marino et al. (2015) showed that leniency **only weakly correlates** with human-rated difficulty, concluding that "current computational metrics should not be used in lieu of user studies."

**Density** captures vertical layering (stacked platforms/hills at the same x-coordinate). **Tile frequency statistics** (counts, means, variances of positions per tile type) form a high-dimensional feature space used in regression models predicting human ratings (Summerville et al., 2017).

**Reachability and negative space** (Summerville et al., 2017; Canossa & Smith, 2015) quantify the fraction of interactive tiles or empty space that a player can actually reach, serving as a quality proxy beyond mere playability.

### 4.2 Expressive Range Analysis (ERA)

Introduced by Smith & Whitehead (2010) and adopted almost universally, ERA is a **characterisation** method rather than a quality metric:

1. Generate a large sample (1,000–10,000 levels).
2. Compute two metrics per level (classically linearity × leniency).
3. Visualise the joint distribution as a 2D histogram / heatmap.
4. Identify peaks (common outputs), holes (gaps in capability), and biases.

ERA has been extended with additional metric pairs (Horn et al., 2014; Shaker et al., 2012), corner plots for multi-metric visualisation (Summerville & Mateas, 2016), constrained traversal of the expressive range space (Bazzaz & Cooper, 2025), and comparative studies across multiple generators (Schaa & Barriga, 2024).

**Strengths:** Reproducible, visual, excellent for debugging generator biases.
**Limitation:** ERA is descriptive — it characterises *what* a generator produces, not whether players enjoy it. As Marino et al. (2015) and Summerville et al. (2017) demonstrate, structural diversity does not imply experiential quality.

### 4.3 Agent-Based Evaluation

Using AI agents as player proxies enables scalable, repeatable assessment of playability and difficulty.

**Playability gates.** A level is deemed playable if a strong agent (typically the A\* controller from the 2009 Mario AI Championship) can complete it. This binary check is the most common first stage in PCG evaluation pipelines (Volz et al., 2018; Nam et al., 2024; Summerville & Mateas, 2016).

**Difficulty proxies.** Agent-derived metrics include:
- **Jump count:** Number of jumps the A\* agent performs, interpreted as difficulty. Volz et al. (2018) modify A\* to make jumps more expensive so that only "required" jumps are counted.
- **Completion fraction:** Progress along the x-axis if the level is not fully completable.
- **Virtual damage:** Nam et al. (2024) introduce stochastic "human-like" agents that model input timing inaccuracies. Difficulty is operationalised as total damage (enemy hits + hole falls), mapped through a piecewise appropriateness function penalising both extremes (too easy / too hard).

**Strengths:** Fast, reproducible, zero participant cost.
**Limitations:** Agent bias is a fundamental concern. Superhuman agents can "solve" levels humans cannot; suboptimal agents may falsely mark levels unplayable. Difficulty estimates depend on the specific agent policy, and results may not generalise to human players (Volz et al., 2018; Nam et al., 2024).

### 4.4 Human Evaluation

Human studies remain the **gold standard** but are expensive and time-consuming.

**Pairwise forced-choice (2AFC).** The Mario AI Championship (Shaker et al., 2011) asked judges to play two levels and answer "which was more fun?" without defining "fun" further. Order effects were controlled by having the same judge play both orders. This protocol directly inspired PCG Arena's design.

**Likert-scale ratings.** Marino et al. (2015) used 7-point Likert scales for enjoyment, visual aesthetics, and difficulty (n = 37). Summerville et al. (2017) collected Likert ratings on 85 metrics to measure inter-rater agreement and determine empirical ceilings for metric–human correlations.

**Large-scale web studies.** Pedersen et al. (2010) recruited 181 subjects via web/social media to play Infinite Mario Bros variants and report pairwise preferences on six affective states (fun, challenge, boredom, frustration, predictability, anxiety). The resulting dataset trained neuroevolutionary models mapping gameplay features to player experience. A follow-up (Shaker et al., 2011b) scaled to 600 players.

**Inter-rater agreement as a ceiling.** Summerville et al. (2017) explicitly measured human-to-human agreement and found that while difficulty ratings achieve moderate reliability, aesthetic judgments are inherently noisier — capping the correlation any automated metric can achieve.

### 4.5 Diversity and Similarity Metrics

**Compression Distance / NCD.** Treating levels as strings and measuring compression savings quantifies structural similarity. Shaker et al. (2012) use gzip-based NCD; values > 0.6 indicate substantial dissimilarity. Horn et al. (2014) adopt the same approach in their benchmark.

**KL-divergence.** Nam et al. (2024) compute KL-divergence over tile-arrangement vectors to quantify diversity within a generated set, integrated into a diversity-aware policy.

**Entropy of spatial distributions.** Shaker et al. (2011) use entropy over enemy/gap counts in equally spaced level segments to capture distributional diversity.

**Pattern density and variation.** Horn et al. (2014) and Dahlskog & Togelius (2014) search for meso-patterns from original SMB levels and report how many distinct patterns appear and how varied they are — proxies for "Mario-like structure" and non-repetitiveness.

### 4.6 Learning-Based Evaluation

Several studies train predictive models mapping metrics to human ratings:

- **Neuroevolutionary preference learning** (Pedersen et al., 2010): MLPs trained via genetic algorithms to predict pairwise affective preferences from gameplay + level features.
- **Feature analysis** (Shaker et al., 2011b): Sequential forward selection identifies which content and gameplay features best predict fun, challenge, and frustration across 600 players.
- **Regression on 85 metrics** (Summerville et al., 2017): LASSO regression predicts human difficulty/enjoyment/aesthetics ratings, with cross-validation to avoid overfitting.
- **Style models** (Guzdial & Riedl, 2016; Summerville et al., 2016): Learned probabilistic models score levels for stylistic similarity to original SMB, correlating with human style judgments.

---

## 5. Consolidated Table: Evaluation Methods in Mario PCG Research (2010–2025)

The table below provides a single-glance overview of evaluation practices across 15 years of Mario PCG research. Each row represents a key paper; columns indicate which evaluation families were employed.

**Legend:**
- **P** = Playability / solvability gate (agent-based)
- **D** = Difficulty proxy (agent-derived jumps, damage, completion)
- **S** = Static structural metrics (linearity, leniency, density, tile stats)
- **Div** = Diversity / similarity (NCD, KL, entropy, pattern metrics)
- **ERA** = Expressive Range Analysis (2D histogram visualisation)
- **H** = Human study (pairwise, Likert, or web-based)
- **ML** = Learned predictor of player experience / quality

| Paper | Year | Method (brief) | P | D | S | Div | ERA | H | ML | Human study scale |
|---|---:|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|
| Smith & Whitehead | 2010 | Launchpad; ERA framework | | | ✓ | | ✓ | | | — |
| Pedersen et al. | 2010 | Player experience models via web study | | | ✓ | | | ✓ | ✓ | n = 120 (web) |
| Shaker et al. (Championship) | 2011 | Mario AI Level Gen. Competition | | ✓ | ✓ | ✓ | | ✓ | | n = 15+ judges |
| Shaker et al. (Features) | 2011 | Feature analysis; preference learning | | | ✓ | | | ✓ | ✓ | n = 600 (web) |
| Shaker et al. (GE) | 2012 | Grammatical Evolution; ERA + NCD | | | ✓ | ✓ | ✓ | | | — |
| Horn et al. / Dahlskog & Togelius | 2014 | Benchmark metrics; pattern metrics | | | ✓ | ✓ | ✓ | | | — |
| Marino et al. | 2015 | User study vs. computational metrics | | | ✓ | ✓ | | ✓ | | n = 37 (web) |
| Summerville & Mateas | 2016 | LSTM level generation; path co-gen | ✓ | ✓ | ✓ | | | | ✓ | — |
| Summerville et al. (Video) | 2016 | LSTM from video traces; style model | | ✓ | ✓ | | | | ✓ | — |
| Shi & Chen | 2016 | Constructive Primitives; learned quality | | | ✓ | | ✓ | | ✓ | Expert annotation |
| Summerville et al. | 2017 | 85 metrics; inter-rater bounds | | ✓ | ✓ | | | ✓ | ✓ | n = dataset-based |
| Volz et al. (MarioGAN) | 2018 | GAN + CMA-ES; LVE | ✓ | ✓ | ✓ | | | | | — |
| Nam et al. | 2024 | PCGRL; human-like agents; DAGP | ✓ | ✓ | ✓ | ✓ | | ✓ | | n = 33 (lab) |
| Schaa & Barriga | 2024 | ERA of 3 open-source generators | | | ✓ | ✓ | ✓ | | | — |
| Bazzaz & Cooper | 2025 | Constrained ERA; quality-diversity | | | ✓ | ✓ | ✓ | | | — |
| **PCG Arena (ours)** | **2026** | **Web-based blind A/B pairwise + tags** | **✓** | **✓** | **✓** | **✓** | | **✓** | **✓** | **n = 27, 571 votes** |

### Key observations from the table

1. **Structural metrics (S) are near-universal** — every paper computes at least linearity or leniency. However, definitions vary and cross-paper numerical comparison is hazardous.
2. **ERA is the dominant characterisation tool** (7/15 papers) but is always purely descriptive.
3. **Human studies are rarer** (7/15) and typically small-scale (15–37 participants in controlled settings; 120–600 via web). PCG Arena's 571 votes from 27 players represents a competitive scale, with the added rigour of blind comparison and Glicko-2 aggregation.
4. **Agent-based playability gates** became standard from 2016 onward but carry agent-bias risks that are rarely quantified.
5. **Learned predictors** appear in 6/15 papers but are usually study-specific; no community-standard reward model exists — a gap PCG Arena's Judge Function aims to fill.
6. **The alignment gap persists.** Marino et al. (2015) concluded that "current computational metrics should not be used in lieu of user studies." Eight years later, no universally accepted metric has bridged this gap, motivating platforms like PCG Arena that collect human preference data at scale.

---

## 6. The Evaluation Gap — Motivation for PCG Arena

The literature reveals a persistent tension between **scalable automated metrics** and **expensive-but-valid human studies**. This tension manifests in three concrete problems that PCG Arena addresses:

### 6.1 Metrics–Experience Misalignment

Marino et al. (2015) showed that two generators rated identically by all computational metrics (linearity, leniency, density, compression distance) were rated **significantly differently** by human players on enjoyment. Leniency — designed to approximate difficulty — only weakly correlated with human-rated difficulty. Summerville et al. (2017) further showed that inter-rater agreement imposes ceilings on achievable metric–human correlations, with aesthetics being particularly noisy.

**PCG Arena's contribution:** By collecting large-scale pairwise preferences in a blind setting, the platform provides ground-truth preference data against which any automated metric can be validated.

### 6.2 Small-N and Lab Bias

Most human studies use 15–37 participants in controlled lab settings (Shaker et al., 2011; Marino et al., 2015). Larger web studies (Pedersen et al., 2010: n = 120–181; Shaker et al., 2011b: n = 600) sacrifice control over conditions. No prior platform offered both scale and blind comparison.

**PCG Arena's contribution:** A persistent web platform supporting blind A/B testing with Glicko-2 uncertainty quantification, enabling ongoing data collection beyond any single study.

### 6.3 Generator Reputation Bias

When players know which algorithm produced a level ("this is MarioGPT"), expectations contaminate judgments. Lab studies rarely blind participants to generator identity.

**PCG Arena's contribution:** Players never see generator names — they play "Level A" and "Level B" — eliminating reputation bias.

### 6.4 Absence of a Community-Standard Reward Model

Search-based and RL-based generators require fitness/reward functions, yet no validated reward model for Mario level quality exists. Existing proxies (leniency, jump count, agent damage) are weakly correlated with human preferences. Experience-driven PCG (Yannakakis & Togelius, 2011) envisions generators optimising empirically derived player models, but the training data — large-scale human preferences over diverse generators — has been unavailable.

**PCG Arena's contribution:** The collected 571 human votes, enriched with gameplay telemetry and subjective tags, serve as training data for the Judge Function (r = 0.736 with human preferences) and for DPO-based generator alignment (MarioDPO).

---

## 7. Summary and Positioning

The PCG literature over the past 15 years has made substantial progress in *generating* Mario levels across paradigms — from grammars and search to GANs, LSTMs, GPT-2, and RL. In contrast, *evaluating* these generators remains fragmented:

- **Structural metrics** are convenient but misaligned with player experience.
- **Agent-based proxies** are scalable but agent-dependent.
- **Human studies** are valid but expensive, small-scale, and rarely blind.
- **Learned models** are promising but trained on limited, study-specific datasets.

PCG Arena addresses this gap by providing a **persistent, blind, web-based platform** for human evaluation at scale, producing the preference data needed to (a) rank generators with statistical confidence, (b) validate and calibrate automated metrics, and (c) train alignment-based generators like MarioDPO.

---

## References

```
Bazzaz, M. & Cooper, S. (2025). Level Generation with Constrained Expressive Range. FDG '25.
Dahlskog, S. & Togelius, J. (2014). Procedural Content Generation Using Patterns as Objectives. EvoApplications 2014.
Horn, B., Dahlskog, S., Shaker, N., Smith, G. & Togelius, J. (2014). A Comparative Evaluation of Procedural Level Generators in the Mario AI Framework. FDG.
Karakovskiy, S. & Togelius, J. (2012). The Mario AI Benchmark and Competitions. IEEE Trans. Computational Intelligence and AI in Games.
Khalifa, A. et al. (2020). PCGRL: Procedural Content Generation via Reinforcement Learning. AIIDE.
Marino, J. R. H., Reis, W. M. P. & Lelis, L. H. S. (2015). An Empirical Evaluation of Evaluation Metrics of Procedurally Generated Mario Levels. AIIDE.
Mawhorter, P. & Mateas, M. (2010). Occupancy-Regulated Extension. PCGames Workshop.
Nam, S.-G., Hsueh, C.-H., Rerkjirattikal, P. & Ikeda, K. (2024). Using RL to Generate Levels of SMB with Quality and Diversity. IEEE Trans. Games, 16(4), 807–820.
Pedersen, C., Togelius, J. & Yannakakis, G. N. (2010). Modeling Player Experience for Content Creation. IEEE Trans. CIAIG, 2(1), 54–67.
Schaa, H. & Barriga, N. A. (2024). Evaluating the Expressive Range of SMB Level Generators. Algorithms, 17(7), 307.
Shaker, N. et al. (2011). The 2010 Mario AI Championship: Level Generation Track. IEEE Trans. CIAIG, 3(4), 332–347.
Shaker, N., Yannakakis, G. N. & Togelius, J. (2011b). Feature Analysis for Modeling Game Content Quality. CIG.
Shaker, N. et al. (2012). Evolving Levels for SMB Using Grammatical Evolution. CIG.
Shi, P. & Chen, K. (2016). Online Level Generation in SMB via Learning Constructive Primitives. CIG.
Smith, G. & Whitehead, J. (2010). Analyzing the Expressive Range of a Level Generator. PCGames '10, ACM.
Sudhakaran, S. et al. (2023). MarioGPT: Open-Ended Text2Level Generation through Large Language Models. NeurIPS.
Summerville, A. & Mateas, M. (2016). Super Mario as a String: Platformer Level Generation via LSTMs. DiGRA/FDG.
Summerville, A. et al. (2016). Learning Player Tailored Content from Observation. AIIDE Workshop.
Summerville, A. et al. (2017). Understanding Mario: An Evaluation of Design Metrics for Platformers. FDG.
Summerville, A. et al. (2018). Procedural Content Generation via Machine Learning (PCGML). IEEE Trans. Games.
Togelius, J. et al. (2011). Search-Based Procedural Content Generation: A Taxonomy and Survey. IEEE Trans. CIAIG, 3(3), 172–186.
Volz, V. et al. (2018). Evolving Mario Levels in the Latent Space of a DCGAN. GECCO.
Yannakakis, G. N. & Togelius, J. (2011). Experience-Driven Procedural Content Generation. IEEE Trans. Affective Computing, 2(3), 147–161.
```
