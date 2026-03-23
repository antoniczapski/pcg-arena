# Rankings, Arenas, and Alignment — Background for Masters Thesis

> **Purpose:** This document synthesises the ranking-systems, arena-evaluation, and alignment (RLHF/DPO) background for the masters thesis *"PCG Arena: A Platform for Blind A/B Testing of Procedural Content Generators with Direct Preference Optimization."* It is structured to map onto thesis Chapter 2 sections `bg-rating` (Rating Systems and Arenas) and `bg-alignment` (RLHF and DPO). Because the thesis's primary subject is PCG, this chapter is kept deliberately concise, foregrounding only the concepts that PCG Arena directly uses or extends.

---

## 1. Paired-Comparison Foundations

All rating and preference-learning systems used in PCG Arena rest on the theory of **paired comparisons** — extracting latent quality scores from binary "A vs B" judgements.

**Thurstone's Law of Comparative Judgment (1927).** Thurstone modelled each stimulus as a normally distributed random variable on an internal psychological continuum. The probability that stimulus $i$ is preferred to stimulus $j$ is:

$$P(i \succ j) = \Phi\!\left(\frac{\mu_i - \mu_j}{\sqrt{\sigma_i^2 + \sigma_j^2}}\right)$$

where $\Phi$ is the standard normal CDF. The widely used *Case V* simplification assumes equal variances across stimuli (Thurstone, 1927; Mikhailiuk et al., 2020).

**The Bradley-Terry Model (1952).** Bradley and Terry recast the comparison as a logistic model: each item $i$ is assigned a positive strength parameter $\pi_i$, and

$$P(i \succ j) = \frac{\pi_i}{\pi_i + \pi_j}.$$

This is equivalent to Thurstone Case V under a logistic (rather than Gaussian) link function and is the default preference model in both Elo-family rating systems and modern RLHF reward models (Bradley & Terry, 1952; Rafailov et al., 2023).

**Relevance to PCG Arena.** Every vote cast in PCG Arena is a single paired comparison between two generator-produced Mario levels. The platform's rating engine (Glicko-2), its matchmaking algorithm (AGIS), and the downstream DPO training all assume a Bradley-Terry preference structure.

---

## 2. Skill-Rating Systems

### 2.1 The Elo System

Elo (1978) operationalised Bradley-Terry for competitive chess. Each player carries a scalar rating $R$; the expected score of player $A$ against player $B$ is

$$E_A = \frac{1}{1 + 10^{(R_B - R_A)/400}}.$$

After an observed outcome $S_A \in \{0, 0.5, 1\}$, the rating updates as $R_A' = R_A + K(S_A - E_A)$, where $K$ is a fixed gain constant. Elo's simplicity made it the de facto standard in chess, tennis, and early online games, but its constant $K$ cannot distinguish a reliable veteran from a new entrant (Elo, 1978).

### 2.2 Glicko and Glicko-2

**Glicko (Glickman, 1999).** Glickman recast Elo in a Bayesian framework. Each player's rating is described by a Gaussian distribution $\mathcal{N}(\mu, \sigma^2)$, where $\sigma$ — the *ratings deviation* (RD) — quantifies uncertainty. After each rating period (a batch of games), the posterior mean and variance are updated via approximate Bayesian inference. Between periods, RD grows to reflect increased uncertainty from inactivity. The model is a non-linear state-space formulation of paired comparisons, applied to over 30,000 USCF chess players and validated on ATP tennis data (Glickman, 1999).

**Glicko-2 (Glickman, 2012).** Glicko-2 adds a third parameter, *volatility* $\sigma_v$, which captures how erratic a player's performance is from period to period. Volatility is estimated iteratively (via the Illinois algorithm) and modulates how quickly uncertainty grows between rating periods. The update pipeline is:

1. Convert ratings to the Glicko-2 internal scale ($\mu' = (\mu - 1500)/173.7178$).
2. Compute estimated variance $v$ and improvement factor $\Delta$ from outcomes.
3. Update volatility $\sigma_v'$ using the iterative convergence algorithm.
4. Update RD: $\phi' = 1/\sqrt{1/\phi^{*2} + 1/v}$, where $\phi^* = \sqrt{\phi^2 + \sigma_v'^2}$.
5. Update rating: $\mu' \leftarrow \mu' + \phi'^2 \sum_j g(\phi_j)(\,s_j - E_j)$.

Glicko-2 is the rating system used by PCG Arena. Generators and levels are treated as "players"; each human vote corresponds to a match outcome. RD provides a built-in measure of rating reliability, and volatility accommodates generators whose perceived quality shifts as new levels are added (Glickman, 2012; Sarkar et al., 2017).

### 2.3 TrueSkill

TrueSkill (Herbrich et al., 2006) generalises Glicko ideas to team games and free-for-all settings using factor-graph inference. Each player has a Gaussian skill belief $\mathcal{N}(\mu, \sigma^2)$; inference is performed via Expectation Propagation. TrueSkill supports draws, multi-team matches, and partial-play, and was deployed at scale on Xbox Live. While PCG Arena uses 1-vs-1 comparisons (making TrueSkill's team extensions unnecessary), TrueSkill demonstrates that Bayesian paired-comparison models scale to millions of participants (Herbrich et al., 2006).

---

## 3. Adaptive Pairing and Matchmaking

Naïvely comparing all $\binom{n}{2}$ pairs is infeasible when the number of conditions $n$ is large or each comparison is expensive. Adaptive pairing algorithms select the *most informative* next pair, reducing the total number of comparisons needed to reach a target accuracy.

### 3.1 Information-Gain Maximisation

Glickman & Jensen (2005) proposed selecting pairs that maximise the expected Kullback-Leibler divergence between the current and updated posterior — a Bayesian optimal experimental design criterion. Mikhailiuk et al. (2020) extended this idea with **ASAP** (Active Sampling for Pairwise comparisons), combining approximate message passing for full posterior updates with information-gain-based pair selection in batch mode. On both synthetic and perceptual-quality data, ASAP outperformed partial-update baselines (Crowd-BT, Hybrid-MST, TrueSkill sampling) in accuracy per comparison (Glickman & Jensen, 2005; Mikhailiuk et al., 2020).

### 3.2 Dueling Bandits

Yue et al. (2012) formalised the **K-armed dueling bandits problem**: an online learner must identify the best of $K$ options using only noisy pairwise comparisons. Their *Interleaved Filter* algorithm achieves information-theoretically optimal regret under the Bradley-Terry and Gaussian comparison models. The framework is directly applicable to any system — including PCG Arena — that must allocate a limited comparison budget across many candidates (Yue et al., 2012).

### 3.3 Application to Human Computation Games

Sarkar et al. (2017) applied Glicko-2 to the human computation game *Paradox*, treating both players and puzzle-tasks as rated entities. Matchmaking-based ordering led to significantly more attempted and completed levels than random ordering ($n = 294$). This work is the most direct precedent for PCG Arena's design: it demonstrated that player-rating systems can estimate both human skill and task difficulty simultaneously, enabling adaptive difficulty balancing in games — exactly the dual-rating architecture PCG Arena adopts for generators and levels (Sarkar et al., 2017).

### 3.4 PCG Arena's AGIS Algorithm

PCG Arena synthesises these ideas into **AGIS** (Adaptive Generator-Informed Sampling). AGIS selects the next pair of levels to present to a player by combining (a) the Glicko-2 uncertainty of candidate levels (preferring under-rated levels), (b) the similarity of candidate ratings (preferring close matches for maximal information gain), and (c) generator diversity (avoiding repeated generator match-ups). AGIS can be seen as a practical, domain-specific instantiation of the information-gain principle (Glickman & Jensen, 2005) with additional coverage constraints.

---

## 4. Arena-Style Evaluation Platforms

The **arena paradigm** — collecting anonymous pairwise votes from a crowd to rank competing systems — has recently been adopted outside games.

**Chatbot Arena (Chiang et al., 2024).** LMSYS Org deployed a web platform where users chat simultaneously with two anonymous LLMs and vote for the better response. Over 240,000 votes from 90,000+ users across 50+ models and 100+ languages have been collected. Rankings are computed via a Bradley-Terry model with maximum-likelihood estimation. An active sampling strategy concentrates votes on model pairs whose ratings are close, mirroring the information-gain logic of Glickman & Jensen (2005). Chatbot Arena validated crowd-vs-expert agreement and is the closest structural analogue to PCG Arena outside the games domain (Chiang et al., 2024).

**LLM-as-a-Judge (Zheng et al., 2023).** Zheng et al. systematically studied using a strong LLM (GPT-4) as a surrogate judge for pairwise and single-answer evaluation. GPT-4 achieved >80% agreement with human preferences — matching inter-human agreement. The authors identified position bias, verbosity bias, and self-enhancement bias, proposing mitigations (answer swapping, reference-guided grading). PCG Arena's *Judge Function* — a lightweight model predicting which of two Mario levels a human would prefer — plays an analogous role to LLM-as-a-Judge, providing scalable automated evaluation once enough human votes have been collected (Zheng et al., 2023).

**Crowdsourcing Quality.** Snow et al. (2008) showed that aggregating labels from multiple non-expert annotators on Amazon Mechanical Turk can match expert-level quality across five NLP tasks, with a bias-correction technique further improving reliability. This finding underpins the design assumption of all arena platforms: that a sufficient number of non-expert pairwise votes, properly aggregated, yields a trustworthy ranking (Snow et al., 2008).

---

## 5. Reinforcement Learning from Human Feedback (RLHF)

RLHF trains a policy to maximise a reward signal derived from human preferences rather than a hand-designed reward function. The core pipeline crystallised over a sequence of four landmark papers:

| Step | Paper | Key contribution |
|------|-------|-----------------|
| 1 | Christiano et al., 2017 | Proposed learning a reward model $\hat{r}$ from human pairwise comparisons of trajectory segments, then optimising the policy against $\hat{r}$. Three asynchronous processes: policy rollouts → human labelling → reward model training. Applied to Atari and MuJoCo with <1% of interactions requiring human feedback. |
| 2 | Ziegler et al., 2019 | Adapted the scheme to language models (774M GPT-2). Introduced a KL penalty $\beta\,\text{KL}[\pi \| \pi_{\text{ref}}]$ to prevent the policy from drifting far from the pretrained model. Used 5K–60K human comparisons depending on the task. |
| 3 | Stiennon et al., 2020 | Scaled to summarisation (6.7B model, 64,832 comparisons). Showed that the learned reward model predicts human preferences better than ROUGE, confirming the "metric mismatch" problem — automatic metrics are rough proxies for true quality. |
| 4 | Ouyang et al. (InstructGPT), 2022 | Codified the three-step recipe: *SFT → Reward Model → PPO*. A 1.3B InstructGPT was preferred over a 175B GPT-3 (85±3% win rate), demonstrating that alignment quality matters more than raw scale. Used 40 human contractors. |

**Motivation for PCG Arena.** The RLHF pipeline addresses the same fundamental problem as PCG Arena: *metric mismatch*. Just as ROUGE fails to capture summary quality (Stiennon et al., 2020), automated PCG metrics (e.g., A* solvability, tile-pattern frequency) fail to capture fun, aesthetics, or challenge appropriateness (Shaker et al., 2010). PCG Arena's paired-comparison voting is the game-design analogue of RLHF's preference collection phase.

---

## 6. Direct Preference Optimisation (DPO)

Rafailov et al. (2023) observed that the optimal RLHF policy can be expressed in closed form as a function of the reward model, which is itself parameterised via Bradley-Terry. Substituting this closed-form solution back into the reward-model loss yields **DPO**, a simpler objective that directly fine-tunes the policy using preference pairs — eliminating the reward model and the RL loop entirely:

$$\mathcal{L}_{\text{DPO}}(\pi_\theta; \pi_{\text{ref}}) = -\mathbb{E}_{(x,\,y_w,\,y_l)}\!\left[\log\sigma\!\left(\beta\log\frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta\log\frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)\right]$$

where $y_w$ and $y_l$ are the preferred and dispreferred completions and $\beta$ controls the deviation from the reference policy $\pi_{\text{ref}}$. The gradient implicitly increases the likelihood of preferred outputs and decreases the likelihood of dispreferred ones, weighted by how much the current policy already agrees. DPO matched or exceeded PPO-based RLHF on sentiment, summarisation, and dialogue tasks while being simpler to implement and more stable to train (Rafailov et al., 2023).

**PCG Arena's MarioDPO.** The MarioDPO generator applies DPO to Mario level generation. Preference pairs are constructed from PCG Arena votes: the level receiving the human vote becomes $y_w$, the other becomes $y_l$. The DPO objective then fine-tunes a base level generator to produce levels more aligned with human preferences, closing the loop from human evaluation back to generation.

---

## 7. AI Feedback and Scalable Oversight

Collecting human preferences is expensive. Two lines of work explore replacing or supplementing human labellers with AI:

**Constitutional AI / RLAIF (Bai et al., 2022).** Anthropic's Constitutional AI replaces human harmlessness labels with AI self-critique and revision guided by a set of natural-language principles (a "constitution"). In the RL phase, a preference model is trained on AI-generated comparisons (RLAIF). The resulting models were preferred over standard RLHF models by crowdworkers while requiring no human labels for harmlessness — demonstrating that AI feedback can substitute for human feedback when guided by explicit principles (Bai et al., 2022).

**RLAIF vs RLHF (Lee et al., 2023).** Lee et al. directly compared RLAIF and RLHF across summarisation, helpful dialogue, and harmless dialogue. RLAIF achieved statistically indistinguishable win rates from RLHF in head-to-head human evaluation. They also introduced *direct-RLAIF* (d-RLAIF), which skips reward-model training and obtains rewards directly from an LLM during RL, further simplifying the pipeline. These results suggest that LLM-generated preference labels are a scalable substitute for human labels (Lee et al., 2023).

**Preference-based RL Survey (Abdelkareem et al., 2024).** Abdelkareem et al. provide a unified framework for preference-based RL (PbRL), covering trajectory-preference types, reward-model architectures (linear and DNN-based), and both online and offline RL formulations. The survey catalogues the full lineage from early Bayesian policy learning through Christiano et al.'s DNN reward model to modern DPO, and identifies open challenges including feedback efficiency and non-stationary preferences — issues directly relevant to PCG Arena's incremental data collection (Abdelkareem et al., 2024).

**Relevance to PCG Arena.** PCG Arena's Judge Function is a domain-specific RLAIF analogue: once trained on sufficient human votes, it can generate synthetic preference labels for generator pairs that have not yet been human-evaluated, enabling DPO training on a larger effective dataset.

---

## 8. Ethics of Online A/B Experiments

PCG Arena is, at its core, an online controlled experiment. Two works inform its ethical design:

**Kohavi et al. (2013)** describe Microsoft Bing's experimentation platform, which runs 200+ concurrent A/B tests over ~100 million monthly users. They discuss cultural, engineering, and trustworthiness challenges at scale — including the value of running *negative* experiments (ones that temporarily degrade user experience) to measure learning value. Their practical guidelines on statistical interactions, alerting, and overall evaluation criteria (OEC) directly influenced PCG Arena's experimental infrastructure (Kohavi et al., 2013).

**Polonioli et al. (2023)** propose a soft-ethics governance framework for A/B testing based on four principles adapted from bioethics: *autonomy*, *fairness*, *non-maleficence*, and *beneficence*. They argue that companies conducting online experiments bear ethical responsibilities analogous to those of academic researchers, and provide a checklist of prompting questions for practitioners. PCG Arena addresses these principles through informed consent, anonymisation of player data, and transparent disclosure of the study's purpose (Polonioli et al., 2023).

---

## 9. Summary and Thesis Integration

The table below maps each reviewed concept to its role in PCG Arena and the corresponding thesis section.

| Concept | Key references | Role in PCG Arena | Thesis section |
|---|---|---|---|
| Paired comparisons (Bradley-Terry) | Bradley & Terry, 1952; Thurstone, 1927 | Preference model underlying ratings, matchmaking, and DPO | §bg-rating |
| Elo rating system | Elo, 1978 | Historical predecessor; motivates Glicko-2's improvements | §bg-elo |
| Glicko-2 | Glickman, 1999; 2012 | Rating engine for generators and levels | §bg-glicko2 |
| TrueSkill | Herbrich et al., 2006 | Bayesian skill-rating comparator (team games) | §bg-elo |
| Adaptive pairing / AGIS | Glickman & Jensen, 2005; Mikhailiuk et al., 2020; Yue et al., 2012 | AGIS matchmaking algorithm | §bg-arenas |
| Rating-based matchmaking in games | Sarkar et al., 2017 | Direct design precedent (Glicko-2 for task difficulty) | §bg-arenas |
| Chatbot Arena | Chiang et al., 2024 | Structural analogue outside games | §bg-arenas |
| LLM-as-a-Judge | Zheng et al., 2023 | Analogue for Judge Function | §bg-arenas |
| Crowdsourcing quality | Snow et al., 2008 | Validates non-expert aggregation | §bg-arenas |
| RLHF pipeline | Christiano et al., 2017; Ziegler et al., 2019; Stiennon et al., 2020; Ouyang et al., 2022 | Motivation and theoretical basis for preference-driven generation | §bg-rlhf |
| DPO | Rafailov et al., 2023 | MarioDPO training objective | §bg-dpo |
| Constitutional AI / RLAIF | Bai et al., 2022; Lee et al., 2023 | Inspires Judge Function as AI feedback source | §bg-rlhf |
| PbRL survey | Abdelkareem et al., 2024 | Contextualises preference-based RL landscape | §bg-rlhf |
| Ethics of A/B testing | Kohavi et al., 2013; Polonioli et al., 2023 | Ethical framework for the platform | §bg-arenas |
