# Seed Generators — Background for Masters Thesis

> **Purpose:** This document describes the 15 generators (13 algorithmic + 1 human-authored baseline + 1 DPO-aligned) used as seeds in *PCG Arena: A Platform for Blind A/B Testing of Procedural Content Generators with Direct Preference Optimization.* The generators were chosen to benchmark a broad cross-section of established PCG approaches — from early constructive methods through search-based evolution to modern neural generation — so that the arena's preference data reflects the full spectrum of the field.

---

## 1. Selection Rationale

PCG Arena required an initial pool of generators satisfying three criteria:

1. **Methodological diversity.** The pool should span all major PCG paradigms (constructive, search-based, chunk-based, ML-based) to test whether human preferences correlate with algorithmic family.
2. **Established baselines.** Every generator (except MarioDPO, which the thesis itself produces) has been published in peer-reviewed venues or is the official reference implementation of its framework, ensuring reproducibility and scientific credibility.
3. **Compatibility with the Mario AI Framework.** All generators output levels in the tile-grid format of *Infinite Mario Bros* (Karakovskiy & Togelius, 2012), making them directly playable in the arena's browser-based front-end.

The generators fall into five families, summarised in Section 2 and compared in Section 3.

---

## 2. Generator Descriptions

### 2.1 Human-Authored Baseline

**Original SMB1 Levels** — The 15 hand-authored levels from Nintendo's *Super Mario Bros.* (1985), manually transcribed into the Mario AI Framework's tile representation. These levels are not algorithmically generated; they serve as the quality ceiling against which all generators are measured. In the arena, they consistently achieve the highest win rates, confirming that the voting population can discriminate genuine design quality (Nintendo, 1985).

### 2.2 Constructive / Probabilistic Generators

These generators build levels left-to-right by sequentially placing components according to probability distributions. They are fast, always produce completable levels, but offer limited stylistic control.

**Notch (Infinite Mario Bros) Generator** — The default generator shipped with Markus Persson's *Infinite Mario Bros* (2008), embedded in the Mario AI Framework. It iterates through five section templates (*straight*, *hill*, *tubes*, *jump*, *cannons*), selecting each with fixed probabilities and adding basic playability checks. It serves as the most familiar baseline for both researchers and players (Persson, 2008; Karakovskiy & Togelius, 2012).

**Parameterized Notch (NotchParam)** — Extends the Notch generator by exposing six tunable parameters: number of gaps, gap width, number of enemies, enemy placement, number of power-ups, and number of boxes. By sweeping high/low combinations of these parameters, researchers can systematically explore the difficulty–style space. This demonstrates how simple constructive PCG can be made *controllable* (Shaker et al., 2011).

**Randomized Parameterized Notch (NotchParamRand)** — Uses the same parameterized engine but randomly samples a parameter configuration for each generated level, producing high intra-generator variety at zero extra algorithmic cost (Shaker et al., 2011).

**Hopper** — Developed for the 2010 Mario AI Championship Level Generation Track. Like Notch, it writes levels left-to-right with probabilistic placement, but alternates generated segments with pre-designed segments and supports *adaptive* probability adjustment based on player performance. This makes it a rare example of a constructive generator with built-in dynamic difficulty adjustment (Shaker et al., 2011).

### 2.3 Chunk-Based / Assembly Generator

**Occupancy-Regulated Extension (ORE)** — A domain-general geometry-assembly algorithm that builds levels by iteratively attaching hand-authored chunks (42 pieces, up to 10 × 10 tiles) at compatible "anchor points" — positions the player might occupy during play. Occupancy regulation prevents incoherent layouts while preserving design variety. ORE entered the 2010 CIG Level Generation competition and produces stylistically distinctive levels that differ markedly from original Mario, showcasing how chunk reuse can combine human creativity with algorithmic arrangement (Mawhorter & Mateas, 2010).

### 2.4 Search-Based / Evolutionary Generators

These generators encode levels as candidate solutions and optimise them via evolutionary algorithms against hand-crafted fitness functions.

**Grammatical Evolution (GE) Generator** — Levels are encoded as sequences of grammar-expansion instructions (e.g., `gap(x, y, w)`, `hill(x, y, w)`, `tube(x, y, h)`). A genetic algorithm evolves populations of these sequences; fitness rewards many placed game elements while penalising placement conflicts. The context-free grammar ensures syntactic validity by construction. GE achieves high leniency (easy levels) and low linearity (complex vertical structure) (Shaker et al., 2012).

**Pattern-Based Generator — Pattern Count Fitness** — Levels are represented as sequences of 1-tile-wide *micro-patterns* (vertical slices) taken from the original SMB levels. An evolutionary search maximises the *count* of specified *meso-patterns* (multi-column design templates). This variant rewards frequency of pattern occurrence, tending to produce levels that heavily reuse popular motifs (Dahlskog & Togelius, 2014).

**Pattern-Based Generator — Pattern Occurrence Fitness** — Same encoding and search as above, but the fitness counts each target meso-pattern *at most once*, rewarding diversity of pattern usage rather than repetition. Levels tend to include many distinct motifs but can appear patchy when rare patterns are forced together (Dahlskog & Togelius, 2014).

**Pattern-Based Generator — Weighted Pattern Count Fitness** — Fitness counts pattern occurrences but weights each by its rarity in the original levels: uncommon patterns receive higher weight, encouraging the generator to include less-typical Mario structures. This variant balances novelty against conformity (Dahlskog & Togelius, 2014).

### 2.5 Machine-Learning / Neural Generators

**MarioGAN (DCGAN + CMA-ES)** — Trains a Deep Convolutional GAN on level segments from the Video Game Level Corpus (a single SMB1 level). The GAN's generator network maps latent vectors to tile segments; CMA-ES then searches the latent space for vectors that optimise a chosen fitness (e.g., target tile distribution, A* agent playability, jump count). This was one of the first neural level generators and demonstrated that combining learned generative models with evolutionary search yields playable, stylistically plausible levels (Volz et al., 2018).

**MarioGPT (Text2Level via GPT-2)** — A fine-tuned DistilGPT-2 model trained on Mario level data at column-level tokenisation. It accepts short natural-language prompts (e.g., *"many pipes, many enemies, little blocks, low elevation"*) and auto-regressively generates complete levels as text strings. A frozen BART encoder provides cross-attention conditioning on the prompt. 88% of generated levels are playable without post-processing. Combined with novelty search, MarioGPT can produce an open-ended stream of diverse levels — the first text-to-level model (Sudhakaran et al., 2023).

**MarioDiffusion (Text-to-Level Diffusion)** — Uses a text-conditioned diffusion model (UNet denoiser) to generate 16 × 16-tile scenes from natural-language captions (e.g., *"flat ground with two pipes and many coins"*). Captions are assigned deterministically from scene features; several text encoders are compared, with a simple custom transformer outperforming larger pretrained models. A mixed-initiative GUI allows designers to compose long levels from individually generated scenes. MarioDiffusion represents the latest generation of multimodal PCG (Schrum et al., 2025).

### 2.6 Preference-Aligned Generator

**MarioDPO** — The thesis's own contribution. A base level generator (GPT-2-based, similar to MarioGPT) is fine-tuned with Direct Preference Optimisation using preference pairs collected from PCG Arena votes. The voted-for level becomes $y_w$, the other $y_l$, and the DPO loss aligns the generator toward human preferences. MarioDPO closes the loop from evaluation back to generation and is the primary novel output of the thesis.

---

## 3. Comparative Overview

The table below compares all 15 generators across key dimensions. The **Paradigm** column uses the taxonomy from the PCG literature (Togelius et al., 2011; Summerville et al., 2018). **Controllability** indicates whether the generator accepts parameters or prompts. **Playability guarantee** notes whether the generator structurally ensures completable levels. **Era** groups generators chronologically to illustrate the field's evolution.

| Generator | ID | Paradigm | Technique | Controllability | Playability guarantee | Training data | Era | Reference |
|---|---|---|---|---|---|---|---|---|
| Original SMB1 | `original` | Human-authored | Manual design | — | By design | — | 1985 | Nintendo, 1985 |
| Notch | `notch` | Constructive | Probabilistic left-to-right | None | Basic checks | — | 2008 | Persson, 2008 |
| Parameterized Notch | `notchParam` | Constructive | Probabilistic + parameters | 6 difficulty/style knobs | Basic checks | — | 2011 | Shaker et al., 2011 |
| Randomized Param Notch | `notchParamRand` | Constructive | Probabilistic + random params | Random per level | Basic checks | — | 2011 | Shaker et al., 2011 |
| Hopper | `hopper` | Constructive | Probabilistic + pre-designed parts | Adaptive probabilities | By design (hybrid) | — | 2010 | Shaker et al., 2011 |
| ORE | `ore` | Chunk-based | Anchor-point assembly | None (chunk library) | Not guaranteed | 42 hand-authored chunks | 2010 | Mawhorter & Mateas, 2010 |
| GE Generator | `genetic` | Search-based | Grammatical evolution (GA) | Via grammar | Fitness-constrained | — | 2012 | Shaker et al., 2012 |
| Pattern Count | `patternCount` | Search-based | Evolutionary (pattern fitness) | Via fitness weights | Not guaranteed | Original SMB micro-patterns | 2014 | Dahlskog & Togelius, 2014 |
| Pattern Occurrence | `patternOccur` | Search-based | Evolutionary (unique patterns) | Via fitness weights | Not guaranteed | Original SMB micro-patterns | 2014 | Dahlskog & Togelius, 2014 |
| Pattern Weighted Count | `patternWeightCount` | Search-based | Evolutionary (rarity-weighted) | Via fitness weights | Not guaranteed | Original SMB micro-patterns | 2014 | Dahlskog & Togelius, 2014 |
| MarioGAN | `mariogan` | ML (GAN + search) | DCGAN + CMA-ES latent search | Fitness function | A* agent validation | 1 SMB1 level (VGLC) | 2018 | Volz et al., 2018 |
| MarioGPT | `mariogpt` | ML (LLM) | Fine-tuned DistilGPT-2 | Text prompts | ~88% playable | SMB levels (tokenised) | 2023 | Sudhakaran et al., 2023 |
| MarioDiffusion | `marioDiffusion` | ML (Diffusion) | Text-conditioned UNet | Text captions | Post-hoc verification | SMB1 + Lost Levels (VGLC) | 2025 | Schrum et al., 2025 |
| MarioDPO | — | ML (LLM + DPO) | GPT-2 + preference alignment | Text prompts + DPO | ~88% playable | PCG Arena votes | 2026 | This thesis |

### 3.1 Expressivity Metrics (Horn et al., 2014)

Horn et al. (2014) provided the first systematic comparative evaluation of Mario AI Framework generators, defining six expressivity metrics. Their results for the generators shared with PCG Arena are reproduced below (mean ± std over 100 generated levels each):

| Generator | Leniency ↑ | Linearity | Density | Pattern Density | Pattern Variation | Compression Dist. |
|---|---|---|---|---|---|---|
| Original SMB1 | 0.61 ± 0.18 | 0.02 ± 0.02 | 0.35 ± 0.37 | 0.14 ± 0.06 | 0.30 ± 0.10 | 0.76 ± 0.11 |
| Notch | 0.67 ± 0.06 | 0.10 ± 0.11 | 0.40 ± 0.16 | 0.13 ± 0.02 | 0.27 ± 0.08 | 0.53 ± 0.03 |
| NotchParam | 0.85 ± 0.06 | 0.04 ± 0.05 | 0.81 ± 0.08 | 0.08 ± 0.03 | 0.24 ± 0.07 | 0.36 ± 0.08 |
| NotchParamRand | 0.86 ± 0.08 | 0.08 ± 0.06 | 0.80 ± 0.10 | 0.08 ± 0.03 | 0.17 ± 0.09 | 0.47 ± 0.08 |
| Hopper | 0.72 ± 0.04 | 0.15 ± 0.16 | 0.60 ± 0.15 | 0.10 ± 0.02 | 0.29 ± 0.05 | 0.65 ± 0.05 |
| ORE | 0.51 ± 0.08 | 0.05 ± 0.06 | 0.43 ± 0.15 | 0.16 ± 0.03 | 0.35 ± 0.05 | 0.73 ± 0.04 |
| GE | 0.84 ± 0.06 | 0.02 ± 0.03 | 0.47 ± 0.16 | 0.10 ± 0.03 | 0.27 ± 0.06 | 0.56 ± 0.04 |
| Pattern Count | 0.63 ± 0.10 | 0.07 ± 0.09 | 0.08 ± 0.05 | 0.39 ± 0.17 | 0.41 ± 0.07 | 0.85 ± 0.04 |
| Pattern Occurrence | 0.60 ± 0.08 | 0.04 ± 0.06 | 0.06 ± 0.09 | 0.08 ± 0.02 | 0.64 ± 0.11 | 0.79 ± 0.08 |
| Pattern Weighted Count | 0.61 ± 0.12 | 0.06 ± 0.08 | 0.09 ± 0.08 | 0.08 ± 0.03 | 0.24 ± 0.07 | 0.86 ± 0.05 |

*Metrics:* **Leniency** = estimated difficulty (1 = easiest). **Linearity** = R² fit of a line to platform endpoints. **Density** = stacked-platform count. **Pattern density** = meso-pattern frequency. **Pattern variation** = unique meso-pattern count. **Compression distance** = gzip-based structural diversity between level pairs.

Key observations:
- The **original levels** have the highest compression distance (most inter-level variety) and moderate leniency, confirming that human designers produce diverse, balanced challenges.
- **Constructive generators** (Notch family) achieve high leniency (easy) and density but low compression distance (self-similar outputs).
- **Pattern-based generators** produce the most pattern-dense and pattern-diverse levels but at very low density (sparse platforms).
- **ORE** is the least lenient (hardest) generator, with high pattern variation and compression distance — its chunk-assembly approach creates structurally complex, challenging levels.

---

## 4. Paradigm Evolution and Thesis Context

The seed generator pool traces the evolution of Mario-level PCG across three eras:

**Era 1 — Constructive methods (2008–2011).** Notch, NotchParam, NotchParamRand, and Hopper represent the first wave: fast, reliable, but limited in expressiveness. They formed the baseline pool for the Mario AI Championship competitions.

**Era 2 — Search-based methods (2012–2014).** GE and the pattern-based generators introduced optimisation-driven design. Fitness functions encode designer intent (element count, pattern coverage, rarity), but designing good fitness functions is itself a research challenge — the very *metric mismatch* problem that motivates PCG Arena.

**Era 3 — Neural methods (2018–2025).** MarioGAN, MarioGPT, and MarioDiffusion leverage deep learning to capture implicit design knowledge from existing levels. Each represents a different generative paradigm (GANs, autoregressive LLMs, diffusion models) and a different control interface (latent-vector search, text prompts, text-captioned scenes). MarioDPO extends this lineage by adding human-preference alignment via DPO.

By including generators from all three eras, PCG Arena tests the central hypothesis of the thesis: **that human preference data, collected via blind A/B voting and aggregated with Glicko-2 ratings, can discriminate generator quality more reliably than automated expressivity metrics alone.**

---

## 5. References

- Dahlskog, S. & Togelius, J. (2014). A Comparative Evaluation of Procedural Level Generators in the Mario AI Framework. *FDG '14*.
- Horn, B., Dahlskog, S., Shaker, N., Smith, G. & Togelius, J. (2014). A Comparative Evaluation of Procedural Level Generators in the Mario AI Framework. *FDG '14*.
- Karakovskiy, S. & Togelius, J. (2012). The Mario AI Benchmark and Competitions. *IEEE Trans. Computational Intelligence and AI in Games*, 4(1), 55–67.
- Mawhorter, P. & Mateas, M. (2010). Procedural Level Generation Using Occupancy-Regulated Extension. *CIG 2010*.
- Persson, M. (2008). Infinite Mario Bros. [Software]. https://github.com/amidos2006/Mario-AI-Framework
- Schrum, J., Kilday, O., Salas, E., Hagan, B. & Williams, R. (2025). Text-to-Level Diffusion Models with Various Text Encoders for Super Mario Bros. *AIIDE 2025*. arXiv:2507.00184.
- Shaker, N., Nicolau, M., Yannakakis, G. N., Togelius, J. & O'Neill, M. (2012). Evolving Levels for Super Mario Bros Using Grammatical Evolution. *CIG 2012*.
- Shaker, N., Togelius, J., Yannakakis, G. N., Weber, B., Shimizu, T., et al. (2011). The 2010 Mario AI Championship: Level Generation Track. *IEEE Trans. Computational Intelligence and AI in Games*, 3(4), 332–347.
- Sudhakaran, S., González-Duque, M., Glanois, C., Freiberger, M., Najarro, E. & Risi, S. (2023). MarioGPT: Open-Ended Text2Level Generation through Large Language Models. *NeurIPS 2023*. arXiv:2302.05981.
- Summerville, A., Snodgrass, S., Guzdial, M., Holmgård, C., Hoover, A. K., et al. (2018). Procedural Content Generation via Machine Learning (PCGML). *IEEE Trans. Games*, 10(3), 257–270.
- Togelius, J., Yannakakis, G. N., Stanley, K. O. & Browne, C. (2011). Search-Based Procedural Content Generation: A Taxonomy and Survey. *IEEE Trans. Computational Intelligence and AI in Games*, 3(3), 172–186.
- Volz, V., Schrum, J., Liu, J., Lucas, S. M., Smith, A. & Risi, S. (2018). Evolving Mario Levels in the Latent Space of a Deep Convolutional Generative Adversarial Network. *GECCO '18*. https://doi.org/10.1145/3205455.3205517.
