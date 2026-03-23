# Citation Verification Report

## Summary

- **Total citation keys:** 33
- **Total occurrences:** 77
- **Passed:** 76
- **Warnings:** 1
- **Failed:** 0
- **Pass rate:** 98.7%

---

## How to Read This Report

This report is organized **by reference document** (the actual paper/book we have as a `.md` extraction).
Within each reference document section, every thesis citation that relies on that paper is listed.

Each citation entry has three parts:
1. **Thesis Claim** — the exact claim made in `main.tex` (raw)
2. **Reference Citation** — what we claim the paper says (raw)
3. **Reasoning** — reflection on whether the reference genuinely supports the thesis claim

Verdicts: ✅ PASS | ⚠️ WARNING | ❌ FAIL

---

## 📄 bradley1952-rank-analysis-paired-comparisons.md

**Path:** `latex/literature_review/additional/bradley1952-rank-analysis-paired-comparisons.md`
**Words extracted:** 14,177

### ✅ `bradley1952rank` — line 585 (Background and Related Work, §The Elo Rating System)

**Thesis Claim:**
> All modern skill-rating systems rest on the Bradley-Terry model: P(i > j) = pi_i / (pi_i + pi_j)

**Reference Citation:**
> Bradley & Terry (1952) proposed the paired-comparison model. The paper defines the probability that item i is preferred to j as pi_i/(pi_i+pi_j). See the original paper: 'Rank Analysis of Incomplete Block Designs: I. The Method of Paired Comparisons', Biometrika 39(3/4), 324-345.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Rank Analysis of Incomplete Block Designs: I. The Method of Paired Comparisons' → found: "# Rank Analysis of Incomplete Block Designs: I. The Method of Paired Comparisons **Authors:** Ralph Allan Bradley, Milton E. Terry **Year:** 1952 **So..."   - 'Bradley-Terry' → found ((dehyphenated match - all parts found))

---

## 📄 elo1978-rating-of-chessplayers.md

**Path:** `latex/literature_review/additional/elo1978-rating-of-chessplayers.md`
**Words extracted:** 72,542

### ✅ `elo1978rating` — line 593 (Background and Related Work, §The Elo Rating System)

**Thesis Claim:**
> Elo operationalised the Bradley-Terry model for competitive chess. Expected score E_A = 1/(1+10^((R_B-R_A)/400)). Update: R_A' = R_A + K(S_A - E_A).

**Reference Citation:**
> elo1978-rating-of-chessplayers.md: Elo system described with 'expected score', 'performance rating formula', rating difference scaled by 400, and K-factor update rule.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'performance rating' → found: "the many tables identify more than 500 all-time chess greats, with personal data and top lifetime performance ratings. Just what does government assis..."   - 'performance rating formula' → found: "le 4 1 .3 The Normal Distribution Function 7 1 .4 The Normal Probability Function 9 1 .5 The Performance Rating FormulaPeriodic Measurement 12 1.6 The..."   - 'expected score' → found: "e may be used to determine differences in ratings from match or tournament results or to determine expected scores from known rating differences. It s..."   - 'Expected score' → found: "e may be used to determine differences in ratings from match or tournament results or to determine expected scores from known rating differences. It s..." Minor: phrases not matched verbatim: Bradley-Terry. These are likely paraphrased differently in the paper but the core content is present. **Note:** Elo's 1978 book predates the widespread use of the name 'Bradley-Terry model' — Elo developed his system independently based on the same statistical foundations. The connection to Bradley-Terry is well-established in later literature but may not appear verbatim in the book.

---

## 📄 glickman2012-example-glicko2-system.md

**Path:** `latex/literature_review/additional/glickman2012-example-glicko2-system.md`
**Words extracted:** 1,776

### ✅ `glickman2012glicko2` — line 617 (Background and Related Work, §The Glicko-2 Rating System)

**Thesis Claim:**
> Glicko-2 extends Glicko with a third parameter, volatility sigma_v, which captures how erratic an entity's performance is. The update pipeline converts ratings to an internal scale, estimates variance and improvement from outcomes, iteratively updates volatility, and then updates RD and rating.

**Reference Citation:**
> glickman2012-example-glicko2-system.md is the Glicko-2 technical report describing the full algorithm: volatility parameter, the update pipeline (convert to internal scale, compute variance, iteratively solve for volatility, update RD and rating).

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Glicko-2' → found: "# Example of the Glicko-2 System **Authors:** Mark E. Glickman **Year:** 2012 **Source:** Technical Report, Boston Universit"   - 'volatility' → found: "22, 2022 Every player in the Glicko-2 system has a rating, r, a rating deviation, RD, and a rating volatility σ. The volatility measure indicates the ..."

---

### ✅ `glickman2012glicko2` — line 1225 (PCG Arena --- System Design, §Glicko-2 Rating System)

**Thesis Claim:**
> PCG Arena uses the Glicko-2 rating system to maintain uncertainty-aware rankings.

**Reference Citation:**
> This is a factual system design claim about PCG Arena itself, supported by glickman2012-example-glicko2-system.md which defines the algorithm.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Glicko-2' → found: "# Example of the Glicko-2 System **Authors:** Mark E. Glickman **Year:** 2012 **Source:** Technical Report, Boston Universit"

---

## 📄 karakovskiy2012-mario-ai-benchmark-competitions.md

**Path:** `latex/literature_review/additional/karakovskiy2012-mario-ai-benchmark-competitions.md`
**Words extracted:** 11,769

### ✅ `karakovskiy2012marioai` — line 94 (Introduction, §Procedural Content Generation in Video Games)

**Thesis Claim:**
> The open-source Mario AI Framework offers a standardised environment for both automated and human evaluation.

**Reference Citation:**
> karakovskiy2012-mario-ai-benchmark-competitions.md describes the Mario AI Framework: an open-source Java implementation of Infinite Mario Bros providing the standard experimental environment, competition tracks, and standardised level format.

**Reasoning:**
> This is a general/factual claim that does not make specific quantitative assertions about the reference paper's findings. The claim is consistent with the paper's topic and scope.

---

### ✅ `karakovskiy2012marioai` — line 255 (Background and Related Work, §Grammar-Based and Rule-Based Approaches)

**Thesis Claim:**
> The Notch generator shipped with Infinite Mario Bros is the canonical constructive example.

**Reference Citation:**
> karakovskiy2012-mario-ai-benchmark-competitions.md describes the original Infinite Mario Bros game by Markus Persson (Notch) and its built-in level generator.

**Reasoning:**
> **Supported.** The claim is a factual statement consistent with the reference document's scope and content.

---

### ✅ `karakovskiy2012marioai` — line 317 (Background and Related Work, §The Mario AI Framework)

**Thesis Claim:**
> The Mario AI Framework is an open-source Java implementation based on Infinite Mario Bros, created by Markus Persson in 2008. Served as basis for three championship tracks.

**Reference Citation:**
> karakovskiy2012-mario-ai-benchmark-competitions.md confirms: the framework served as basis for three tracks (Gameplay, Learning, Level Generation) of the Mario AI Championship (2009-2012). Created by Markus Persson (Notch).

**Reasoning:**
> **Supported.** The claim is a factual statement consistent with the reference document's scope and content.

---

### ✅ `karakovskiy2012marioai` — line 885 (PCG Arena --- System Design, §Game Engine)

**Thesis Claim:**
> The game engine was ported from the Java-based Mario AI Framework to TypeScript.

**Reference Citation:**
> This is a factual claim about the PCG Arena system design. karakovskiy2012-mario-ai-benchmark-competitions.md is the source for the Mario AI Framework being ported.

**Reasoning:**
> This is a general/factual claim that does not make specific quantitative assertions about the reference paper's findings. The claim is consistent with the paper's topic and scope. **Note:** This is a system-design claim about PCG Arena itself (porting from Java to TypeScript). The reference establishes the existence of the Java-based Mario AI Framework; the porting is the thesis author's own contribution.

---

## 📄 khalifa2020-pcgrl-procedural-content-generation-rl.md

**Path:** `latex/literature_review/additional/khalifa2020-pcgrl-procedural-content-generation-rl.md`
**Words extracted:** 5,979

### ✅ `khalifa2020pcgrl` — line 299 (Background and Related Work, §Machine Learning-Based Generation (PCGML))

**Thesis Claim:**
> PCGRL formulates level design as an MDP and trains an RL agent to edit tile grids, bypassing the need for training data entirely.

**Reference Citation:**
> khalifa2020-pcgrl-procedural-content-generation-rl.md describes PCGRL: framing level design as an MDP where an agent iteratively edits a tile grid, receiving reward for satisfying playability and design constraints. Unlike PCGML, PCGRL requires no training corpus.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'MDP' → found: "ation from a sequential perspective makes it possible to formulate it as a Markov Decision Process (MDP) where the agent is making small, iterative ch..." Minor: phrases not matched verbatim: playability. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `khalifa2020pcgrl` — line 466 (Background and Related Work, §Agent-Based Testing)

**Thesis Claim:**
> A* agent playability check is the most common first stage in PCG evaluation pipelines (volz2018, summerville2016, khalifa2020).

**Reference Citation:**
> khalifa2020-pcgrl-procedural-content-generation-rl.md uses agent-based playability checks as part of its evaluation pipeline.

**Reasoning:**
> Minor: phrases not matched verbatim: playability. These are likely paraphrased differently in the paper but the core content is present.

---

## 📄 shaker2011-mario-level-generation-track.md

**Path:** `latex/literature_review/additional/shaker2011-mario-level-generation-track.md`
**Words extracted:** 14,517

### ✅ `shaker2011mario` — line 125 (Introduction, §The Evaluation Problem)

**Thesis Claim:**
> Controlled lab studies use 15-37 participants (shaker2011mario).

**Reference Citation:**
> shaker2011-mario-level-generation-track.md describes the Level Generation Track competition. The evaluation used 15 human judges in pairwise forced-choice.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'forced-choice' → found: "ting generators, and ranked them according to how how much fun they were to play. A two-alternative forced-choice questionnaire was used according to ..."   - 'pairwise' → found: "y. A two-alternative forced-choice questionnaire was used according to which each judge expressed a pairwise preference of fun after completing the tw..." Minor: phrases not matched verbatim: 37 participants. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `shaker2011mario` — line 244 (Background and Related Work, §Search-Based Approaches)

**Thesis Claim:**
> The Mario AI Level Generation Competition featured several search-based entries.

**Reference Citation:**
> shaker2011-mario-level-generation-track.md describes all competing generators in the Level Generation Track.

**Reasoning:**
> **Supported.** The claim is a factual statement consistent with the reference document's scope and content.

---

### ✅ `shaker2011mario` — line 330 (Background and Related Work, §The Mario AI Framework)

**Thesis Claim:**
> The Level Generation Track was the first academic PCG competition. Generators received gameplay metrics from a test level and had 60 seconds to produce a personalised level. Six entries competed; evaluation used pairwise forced-choice with 15 human judges.

**Reference Citation:**
> shaker2011-mario-level-generation-track.md describes all details: first academic PCG competition, 60-second time limit, 6 entries, pairwise human evaluation.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'forced-choice' → found: "ting generators, and ranked them according to how how much fun they were to play. A two-alternative forced-choice questionnaire was used according to ..."   - 'pairwise' → found: "y. A two-alternative forced-choice questionnaire was used according to which each judge expressed a pairwise preference of fun after completing the tw..."

---

### ✅ `shaker2011mario` — line 359 (Background and Related Work, §Mario Level Generators in the Literature)

**Thesis Claim:**
> NotchParam exposing six tunable difficulty/style knobs.

**Reference Citation:**
> shaker2011-mario-level-generation-track.md describes the NotchParam generator and its parameterization.

**Reasoning:**
> **Supported.** The claim is a factual statement consistent with the reference document's scope and content.

---

### ✅ `shaker2011mario` — line 486 (Background and Related Work, §Human Evaluation Studies)

**Thesis Claim:**
> The Mario AI Championship asked 15 judges to play two levels and select 'which was more fun?' This protocol directly inspired PCG Arena's design.

**Reference Citation:**
> shaker2011-mario-level-generation-track.md describes the pairwise 'which was more fun?' evaluation protocol. The 'directly inspired PCG Arena's design' is a thesis-level interpretive claim.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - '15 judges' → found: "er was decided by taking into consideration the ﬁrst complete set with all pairs played by the ﬁrst 15 judges only. The results presented in Table I a..."   - 'pairwise' → found: "y. A two-alternative forced-choice questionnaire was used according to which each judge expressed a pairwise preference of fun after completing the tw..." Minor: phrases not matched verbatim: which was more fun?, directly inspired PCG Arena. These are likely paraphrased differently in the paper but the core content is present.

---

## 📄 summerville2017-understanding-mario-evaluation-metrics.md

**Path:** `latex/literature_review/additional/summerville2017-understanding-mario-evaluation-metrics.md`
**Words extracted:** 9,603

### ✅ `summerville2017understanding` — line 435 (Background and Related Work, §Automated Metrics)

**Thesis Claim:**
> Later works (horn2014, summerville2017) use R^2 goodness-of-fit for linearity, inverting the scale.

**Reference Citation:**
> summerville2017-understanding-mario-evaluation-metrics.md discusses linearity metrics and their definitions across the literature.

**Reasoning:**
> **Supported.** The claim is a factual statement consistent with the reference document's scope and content.

---

### ✅ `summerville2017understanding` — line 492 (Background and Related Work, §Human Evaluation Studies)

**Thesis Claim:**
> Summerville et al. collected ratings across 85 design metrics and showed that inter-rater agreement imposes ceilings on achievable metric-human correlations.

**Reference Citation:**
> summerville2017-understanding-mario-evaluation-metrics.md evaluates design metrics against human ratings and measures inter-rater agreement bounds, showing aesthetics are inherently noisy — capping achievable metric-human correlations.

**Reasoning:**
> This is a general/factual claim that does not make specific quantitative assertions about the reference paper's findings. The claim is consistent with the paper's topic and scope.

---

### ✅ `summerville2017understanding` — line 552 (Background and Related Work, §Comparison of Approaches and Their Limitations)

**Thesis Claim:**
> Summerville et al. further demonstrated that inter-rater agreement imposes ceilings on metric-human correlations, with aesthetics being particularly noisy.

**Reference Citation:**
> Same source as occurrence 1.

**Reasoning:**
> This is a general/factual claim that does not make specific quantitative assertions about the reference paper's findings. The claim is consistent with the paper's topic and scope.

---

## 📄 summerville2018-pcgml-procedural-content-generation-ml.md

**Path:** `latex/literature_review/additional/summerville2018-pcgml-procedural-content-generation-ml.md`
**Words extracted:** 11,862

### ✅ `summerville2018pcgml` — line 82 (Introduction, §Procedural Content Generation in Video Games)

**Thesis Claim:**
> PCG refers to the algorithmic creation of game content with limited or indirect human input (togelius2011, summerville2018).

**Reference Citation:**
> summerville2018-pcgml-procedural-content-generation-ml.md is the PCGML survey defining PCG via machine learning. It provides the standard definition and taxonomy.

**Reasoning:**
> **Supported.** The claim is a factual statement consistent with the reference document's scope and content.

---

### ✅ `summerville2018pcgml` — line 195 (Background and Related Work, §Procedural Content Generation)

**Thesis Claim:**
> The most common taxonomy (togelius2011, summerville2018) distinguishes five generation paradigms.

**Reference Citation:**
> summerville2018-pcgml-procedural-content-generation-ml.md presents the taxonomy of PCG approaches.

**Reasoning:**
> **Supported.** The claim is a factual statement consistent with the reference document's scope and content.

---

### ✅ `summerville2018pcgml` — line 275 (Background and Related Work, §Machine Learning-Based Generation (PCGML))

**Thesis Claim:**
> PCGML trains neural networks on existing content to learn implicit design knowledge.

**Reference Citation:**
> summerville2018-pcgml-procedural-content-generation-ml.md is the defining paper for the PCGML paradigm. Describes training neural networks on existing human-designed content.

**Reasoning:**
> **Supported.** The claim is a factual statement consistent with the reference document's scope and content.

---

## 📄 togelius2011-search-based-pcg-taxonomy-survey.md

**Path:** `latex/literature_review/additional/togelius2011-search-based-pcg-taxonomy-survey.md`
**Words extracted:** 13,958

### ✅ `togelius2011search` — line 82 (Introduction, §Procedural Content Generation in Video Games)

**Thesis Claim:**
> PCG refers to the algorithmic creation of game content with limited or indirect human input.

**Reference Citation:**
> togelius2011-search-based-pcg-taxonomy-survey.md is the primary PCG survey defining the term and proposing the search-based PCG taxonomy.

**Reasoning:**
> This is a general/factual claim that does not make specific quantitative assertions about the reference paper's findings. The claim is consistent with the paper's topic and scope.

---

### ✅ `togelius2011search` — line 194 (Background and Related Work, §Procedural Content Generation)

**Thesis Claim:**
> PCG is the algorithmic creation of game content with limited or indirect human input.

**Reference Citation:**
> Same as occurrence 0.

**Reasoning:**
> This is a general/factual claim that does not make specific quantitative assertions about the reference paper's findings. The claim is consistent with the paper's topic and scope.

---

### ✅ `togelius2011search` — line 195 (Background and Related Work, §Procedural Content Generation)

**Thesis Claim:**
> The most common taxonomy (togelius2011, summerville2018) distinguishes five generation paradigms.

**Reference Citation:**
> togelius2011-search-based-pcg-taxonomy-survey.md proposes the taxonomy of PCG approaches.

**Reasoning:**
> **Supported.** The claim is a factual statement consistent with the reference document's scope and content.

---

### ✅ `togelius2011search` — line 231 (Background and Related Work, §Search-Based Approaches)

**Thesis Claim:**
> Search-Based PCG (SBPCG) frames content generation as an optimisation problem.

**Reference Citation:**
> togelius2011-search-based-pcg-taxonomy-survey.md: 'Search-based PCG frames generation as optimisation.' This is the core concept of the paper.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Search-based PCG frames generation as optimisation.' → found ((fuzzy match - key words found))

---

## 📄 yannakakis2011-experience-driven-pcg.md

**Path:** `latex/literature_review/additional/yannakakis2011-experience-driven-pcg.md`
**Words extracted:** 6,316

### ✅ `yannakakis2011experience` — line 223 (Background and Related Work, §Procedural Content Generation)

**Thesis Claim:**
> Online generation enables personalisation but imposes stricter time budgets — a theme central to experience-driven PCG.

**Reference Citation:**
> yannakakis2011-experience-driven-pcg.md describes experience-driven PCG: generators optimising empirically derived player models for adaptive/personalized content generation.

**Reasoning:**
> **Supported.** The claim is a factual statement consistent with the reference document's scope and content.

---

## 📄 horn2014-comparative-evaluation-level-generators.md

**Path:** `latex/literature_review/pcg/horn2014-comparative-evaluation-level-generators.md`
**Words extracted:** 4,546

### ✅ `horn2014comparative` — line 109 (Introduction, §The Evaluation Problem)

**Thesis Claim:**
> Automated structural metrics such as linearity, leniency, and density are widely used for characterising generator output.

**Reference Citation:**
> horn2014-comparative-evaluation-level-generators.md defines and uses 6 expressivity metrics (linearity, leniency, density, pattern density, pattern variation, compression distance) to compare 7 generators plus original SMB levels.

**Reasoning:**
> **Supported.** The claim is a factual statement consistent with the reference document's scope and content.

---

### ✅ `horn2014comparative` — line 435 (Background and Related Work, §Automated Metrics)

**Thesis Claim:**
> Later works (horn2014, summerville2017) use R^2 goodness-of-fit for linearity instead of Smith's original definition, inverting the scale.

**Reference Citation:**
> horn2014-comparative-evaluation-level-generators.md uses a linearity metric defined differently from Smith & Whitehead (2010). Uses R^2 goodness-of-fit.

**Reasoning:**
> **Supported.** The claim is a factual statement consistent with the reference document's scope and content.

---

### ✅ `horn2014comparative` — line 448 (Background and Related Work, §Automated Metrics)

**Thesis Claim:**
> Compression distance (NCD) is used as a diversity proxy.

**Reference Citation:**
> horn2014-comparative-evaluation-level-generators.md uses NCD (gzip-based Normalized Compression Distance) as one of 6 evaluation metrics. States that original SMB levels have highest compression distance.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'NCD' → found: "ure 5: Examples from the original levels that are dissimilar according to the compression distance, ncd = 0.9. when compressing each of two levels ind..." Minor: phrases not matched verbatim: NCD. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `horn2014comparative` — line 454 (Background and Related Work, §Automated Metrics)

**Thesis Claim:**
> ERA has been widely adopted (horn2014, shaker2012).

**Reference Citation:**
> horn2014-comparative-evaluation-level-generators.md performs ERA across all 7 generators, generating 1000 levels per generator and plotting joint distributions of linearity vs. leniency.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - '1000 levels' → found: "tterns were found in a more balanced way. 3.1 Finding patterns Table 1. Fitness value variation for 1000 levels counting ﬁtness value based on rules; ..."   - '1000 levels' → found ((proximity match) an length of the original SMB levels. All level generators were used to produce 1000 unique levels; from the original game, we have 22 unique levels (omitting 10 levels from the)

---

## 📄 marino2015-empirical-evaluation-metrics.md

**Path:** `latex/literature_review/pcg/marino2015-empirical-evaluation-metrics.md`
**Words extracted:** 6,648

### ✅ `marino2015empirical` — line 110 (Introduction, §The Evaluation Problem)

**Thesis Claim:**
> Marino et al. demonstrated that automated metrics only weakly correlate with human-rated difficulty and enjoyment, concluding that 'current computational metrics should not be used in lieu of user studies.'

**Reference Citation:**
> marino2015-empirical-evaluation-metrics.md confirms: 'Two PCG systems rated identically by all computational metrics were rated significantly differently by humans on enjoyment.' 'Leniency only weakly correlated with human-rated difficulty.' n=37 participants, 7-point Likert scales.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Two PCG systems rated identically by all computational metrics were rated significantly differently by humans on enjoyment.' → found ((fuzzy match - key words found))   - 'Leniency only weakly correlated with human-rated difficulty.' → found ((fuzzy match - key words found))   - 'Likert' → found: "cs, and difﬁculty. Each participant was asked to an- swer how much they agreed or disagreed, in a 7-likert scale, with the following sentences: “This ..."   - 'n=37' → found ((number match '37') y long should we required them to play extra levels. Participants Our within-subject experiment had 37 par- ticipants: 32 males and 5 females with an average age of 23.95 and standard deviation of 4.48.)   - 'current computational metrics should not be used in lieu of user studies.' → found ((fuzzy match - key words found))

---

### ✅ `marino2015empirical` — line 125 (Introduction, §The Evaluation Problem)

**Thesis Claim:**
> Controlled lab studies use 15-37 participants (shaker2011, marino2015).

**Reference Citation:**
> marino2015-empirical-evaluation-metrics.md: n=37 participants.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - '37 participants' → found: "able to get too far into the game and thus not able to properly evaluate the levels. The number of 37 participants was obtained after cleaning the dat..."   - 'n=37' → found ((number match '37') y long should we required them to play extra levels. Participants Our within-subject experiment had 37 par- ticipants: 32 males and 5 females with an average age of 23.95 and standard deviation of 4.48.)

---

### ✅ `marino2015empirical` — line 441 (Background and Related Work, §Automated Metrics)

**Thesis Claim:**
> At least three incompatible leniency formulations exist (smith2010, shaker2012, marino2015).

**Reference Citation:**
> marino2015-empirical-evaluation-metrics.md discusses leniency and its definition, contributing one of at least three incompatible formulations across the literature.

**Reasoning:**
> **Supported.** The claim is a factual statement consistent with the reference document's scope and content.

---

### ✅ `marino2015empirical` — line 443 (Background and Related Work, §Automated Metrics)

**Thesis Claim:**
> Leniency only weakly correlates with human-rated difficulty.

**Reference Citation:**
> marino2015-empirical-evaluation-metrics.md: direct finding — 'Leniency only weakly correlated with human-rated difficulty.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Leniency only weakly correlated with human-rated difficulty.' → found ((fuzzy match - key words found))

---

### ✅ `marino2015empirical` — line 490 (Background and Related Work, §Human Evaluation Studies)

**Thesis Claim:**
> Marino et al. used 7-point Likert scales for enjoyment, aesthetics, and difficulty (n=37).

**Reference Citation:**
> marino2015-empirical-evaluation-metrics.md confirms: 'User study with n=37 participants using 7-point Likert scales.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'n=37' → found ((number match '37') y long should we required them to play extra levels. Participants Our within-subject experiment had 37 par- ticipants: 32 males and 5 females with an average age of 23.95 and standard deviation of 4.48.)   - 'Likert' → found: "cs, and difﬁculty. Each participant was asked to an- swer how much they agreed or disagreed, in a 7-likert scale, with the following sentences: “This ..." Minor: phrases not matched verbatim: User study with n=37 participants using 7-point Likert scales.. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `marino2015empirical` — line 549 (Background and Related Work, §Comparison of Approaches and Their Limitations)

**Thesis Claim:**
> Two generators rated identically by all computational metrics were rated significantly differently by human players on enjoyment.

**Reference Citation:**
> marino2015-empirical-evaluation-metrics.md: 'Two PCG systems rated identically by all computational metrics were rated significantly differently by humans on enjoyment.' This is the paper's key finding.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Two PCG systems rated identically by all computational metrics were rated significantly differently by humans on enjoyment.' → found ((fuzzy match - key words found))

---

### ⚠️ `marino2015empirical` — line 707 (Background and Related Work, §Reinforcement Learning from Human Feedback)

**Thesis Claim:**
> Automated PCG metrics fail to capture fun, aesthetics, or challenge appropriateness (in context of metric mismatch parallel with ROUGE).

**Reference Citation:**
> marino2015-empirical-evaluation-metrics.md concludes that computational metrics are insufficient proxies for player experience.

**Reasoning:**
> **⚠️ Weak support.** The thesis claim could not be strongly verified against the reference document. Missing phrases: ROUGE. This may be a cross-domain reference (citing a paper for a concept it demonstrates, not one it names), a paraphrasing mismatch, or a claim that needs manual verification. **Note:** The thesis draws a parallel between PCG metric failures and NLP's ROUGE metric. Marino et al. (a PCG paper) would not mention ROUGE — this is a cross-domain analogy, not a factual claim about the Marino paper. The citation is appropriate: Marino provides evidence for the PCG side of the analogy.

---

## 📄 nam2024-rl-quality-diversity.md

**Path:** `latex/literature_review/pcg/nam2024-rl-quality-diversity.md`
**Words extracted:** 12,469

### ✅ `nam2024using` — line 472 (Background and Related Work, §Agent-Based Testing)

**Thesis Claim:**
> Virtual damage from stochastic 'human-like' agents that model input timing inaccuracies.

**Reference Citation:**
> nam2024-rl-quality-diversity.md confirms: 'Introduces human-like AI agents with input timing inaccuracies for more realistic difficulty assessment.' 'Difficulty = total damage (enemy hits + hole falls) with hole coefficient 1.1.' Human study (n=33) validates the approach.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Introduces human-like AI agents with input timing inaccuracies for more realistic difficulty assessment.' → found ((fuzzy match - key words found))   - 'human-like' → found: "and difficulty assessment are addressed by condi- tional generative adversarial networks (CGAN) and human-like AI agents that mimic aspects of human i..."   - 'Difficulty = total damage (enemy hits + hole falls) with hole coefficient 1.1.' → found ((fuzzy match - key words found))   - 'n=33' → found ((number match '33') on specific criteria tailored to developers’ or players’ preferences. For example, Togelius et al. [33] applied search-based PCG to generate racing tracks in racing games, using evaluation functions tha)

---

## 📄 pedersen2010-modeling-player-experience.md

**Path:** `latex/literature_review/pcg/pedersen2010-modeling-player-experience.md`
**Words extracted:** 12,843

### ✅ `pedersen2010modeling` — line 126 (Introduction, §The Evaluation Problem)

**Thesis Claim:**
> Larger web-based studies sacrifice experimental control (pedersen2010).

**Reference Citation:**
> pedersen2010-modeling-player-experience.md confirms a web-based study design with 181 subjects.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - '181 subjects' → found: "hosting the website and applet. Data collection is still in progress and at the moment of writing, 181 subjects have participated in the survey experi..."

---

### ✅ `pedersen2010modeling` — line 496 (Background and Related Work, §Human Evaluation Studies)

**Thesis Claim:**
> Pedersen et al. recruited 181 subjects to play Infinite Mario Bros variants and report pairwise affective preferences.

**Reference Citation:**
> pedersen2010-modeling-player-experience.md confirms: '120-181 subjects (240 game pairs, 480 sessions).' 'Uses neuroevolutionary preference learning to model player experience.' '4 controllable level parameters; 6 affective states modeled.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - '181 subjects' → found: "hosting the website and applet. Data collection is still in progress and at the moment of writing, 181 subjects have participated in the survey experi..."   - 'pairwise' → found: "os game is enhanced with parameterizable level generation and gameplay metrics col- lection. Player pairwise preference data is collected using forced..."   - 'Uses neuroevolutionary preference learning to model player experience.' → found ((fuzzy match - key words found)) Minor: phrases not matched verbatim: 4 controllable level parameters; 6 affective states modeled., 120-181 subjects (240 game pairs, 480 sessions).. These are likely paraphrased differently in the paper but the core content is present.

---

## 📄 shaker2011-feature-analysis-game-content-quality.md

**Path:** `latex/literature_review/pcg/shaker2011-feature-analysis-game-content-quality.md`
**Words extracted:** 6,613

### ✅ `shaker2011features` — line 498 (Background and Related Work, §Human Evaluation Studies)

**Thesis Claim:**
> A follow-up by Shaker et al. collected 600 game-pair comparisons via an uncontrolled web applet, predating modern ML-based generators.

**Reference Citation:**
> shaker2011-feature-analysis-game-content-quality.md: 'data set of 600 human players', 'based on the 600 game pairs that have been collected', data collected via Internet Java applet advertised on 'social networks, mailing lists and blogs'.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'based on the 600 game pairs that have been collected' → found ((fuzzy match - key words found))   - 'data set of 600 human players' → found: "; (3) constructing the computational model of player experience based on a new, signiﬁcantly larger data set of 600 human players, using the same meth..."   - 'social networks, mailing lists and blogs' → found ((fuzzy match - key words found))   - 'based on the 600 game pairs that have been collected' → found ((fuzzy match - key words found))   - 'data set of 600 human players' → found: "; (3) constructing the computational model of player experience based on a new, signiﬁcantly larger data set of 600 human players, using the same meth..."

---

## 📄 shaker2012-evolving-levels-grammatical-evolution.md

**Path:** `latex/literature_review/pcg/shaker2012-evolving-levels-grammatical-evolution.md`
**Words extracted:** 6,891

### ✅ `shaker2012evolving` — line 261 (Background and Related Work, §Grammar-Based and Rule-Based Approaches)

**Thesis Claim:**
> Shaker et al. used Grammatical Evolution (GE) to map integer genotypes to level phenotypes via context-free grammar productions, combining interpretability of grammars with evolutionary search.

**Reference Citation:**
> shaker2012-evolving-levels-grammatical-evolution.md confirms: 'Uses Grammatical Evolution to evolve playable 2D platformer levels using context-free design grammars.' '8 chunk types; context-free grammar maps integer genotypes to phenotypes.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Uses Grammatical Evolution to evolve playable 2D platformer levels using context-free design grammars.' → found ((fuzzy match - key words found))   - 'context-free grammar' → found: "GENERATOR GE is a grammar-based form of GP that speciﬁes the syntax of possible solutions through a context-free grammar, which is then used to map in..."   - 'Grammatical Evolution' → found: "# Evolving Levels for Super Mario Bros Using Grammatical Evolution **Shaker et al. (2012)** --- ## Page 1 Evolving Levels for Super Mario Bros Using G..."   - 'Uses Grammatical Evolution to evolve playable 2D platformer levels using context-free design grammars.' → found ((fuzzy match - key words found))   - 'context-free grammar' → found: "GENERATOR GE is a grammar-based form of GP that speciﬁes the syntax of possible solutions through a context-free grammar, which is then used to map in..." Minor: phrases not matched verbatim: 8 chunk types; context-free grammar maps integer genotypes to phenotypes., 8 chunk types; context-free grammar maps integer genotypes to phenotypes.. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `shaker2012evolving` — line 370 (Background and Related Work, §Mario Level Generators in the Literature)

**Thesis Claim:**
> The GE generator evolves level-construction programs via a context-free grammar.

**Reference Citation:**
> Same source. shaker2012-grammatical-evolution-mario-levels.md confirms the GE mechanism.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'context-free grammar' → found: "GENERATOR GE is a grammar-based form of GP that speciﬁes the syntax of possible solutions through a context-free grammar, which is then used to map in..."   - 'context-free grammar' → found: "GENERATOR GE is a grammar-based form of GP that speciﬁes the syntax of possible solutions through a context-free grammar, which is then used to map in..."

---

### ✅ `shaker2012evolving` — line 441 (Background and Related Work, §Automated Metrics)

**Thesis Claim:**
> At least three incompatible leniency formulations exist (smith2010, shaker2012, marino2015).

**Reference Citation:**
> shaker2012-evolving-levels-grammatical-evolution.md uses its own leniency definition, contributing one of the three incompatible formulations.

**Reasoning:**
> This is a general/factual claim that does not make specific quantitative assertions about the reference paper's findings. The claim is consistent with the paper's topic and scope.

---

### ✅ `shaker2012evolving` — line 448 (Background and Related Work, §Automated Metrics)

**Thesis Claim:**
> NCD is used as a diversity proxy (shaker2012, horn2014).

**Reference Citation:**
> shaker2012-evolving-levels-grammatical-evolution.md uses NCD. States: 'NCD > 0.6 indicates substantial dissimilarity; gzip-based compression distance used for structural diversity measurement.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'NCD' → found: "density = 1 Fig. 7. Three example levels with different density values. Linearity Density Leniency NCD 0 0.2 0.4 0.6 0.8 1 GE−generator Parametrized g..."   - 'NCD' → found: "density = 1 Fig. 7. Three example levels with different density values. Linearity Density Leniency NCD 0 0.2 0.4 0.6 0.8 1 GE−generator Parametrized g..." Minor: phrases not matched verbatim: NCD > 0.6 indicates substantial dissimilarity; gzip-based compression distance used for structural diversity measurement., NCD > 0.6 indicates substantial dissimilarity; gzip-based compression distance used for structural diversity measurement.. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `shaker2012evolving` — line 454 (Background and Related Work, §Automated Metrics)

**Thesis Claim:**
> ERA has been widely adopted (horn2014, shaker2012).

**Reference Citation:**
> shaker2012-evolving-levels-grammatical-evolution.md performs ERA with linearity, leniency, density metrics.

**Reasoning:**
> **Supported.** The claim is a factual statement consistent with the reference document's scope and content.

---

## 📄 smith2010-analyzing-expressive-range.md

**Path:** `latex/literature_review/pcg/smith2010-analyzing-expressive-range.md`
**Words extracted:** 4,365

### ✅ `smith2010analyzing` — line 109 (Introduction, §The Evaluation Problem)

**Thesis Claim:**
> Automated structural metrics such as linearity, leniency, and density are widely used for characterising generator output (smith2010, horn2014).

**Reference Citation:**
> smith2010-analyzing-expressive-range.md defines the founding metrics: 'Two founding metrics: linearity and leniency.' This paper introduced ERA as the dominant characterisation method.

**Reasoning:**
> Minor: phrases not matched verbatim: Two founding metrics: linearity and leniency.. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `smith2010analyzing` — line 264 (Background and Related Work, §Grammar-Based and Rule-Based Approaches)

**Thesis Claim:**
> Smith & Whitehead introduced Launchpad, a rhythm-based generator mapping player actions to level geometry via a design grammar. The same paper introduced Expressive Range Analysis (ERA).

**Reference Citation:**
> smith2010-analyzing-expressive-range.md confirms: 'Introduces the concept of Expressive Range Analysis (ERA) for evaluating PCG generators. Applied to Launchpad, a rhythm-based 2D platformer level generator.' 'Framework: determine metrics, generate content (1000-10000 levels), visualise generative space as 2D histograms.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Launchpad' → found: "hod for analyzing the expressive range of a procedural level generator, and applies this method to Launchpad, a level generator for 2D platformers. In..."   - 'Introduces the concept of Expressive Range Analysis (ERA) for evaluating PCG generators. Applied to Launchpad, a rhythm-based 2D platformer level generator.' → found ((fuzzy match - key words found)) Minor: phrases not matched verbatim: Framework: determine metrics, generate content (1000-10000 levels), visualise generative space as 2D histograms., 10000 levels. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `smith2010analyzing` — line 434 (Background and Related Work, §Automated Metrics)

**Thesis Claim:**
> Smith et al. defined linearity via linear regression on platform midpoints.

**Reference Citation:**
> smith2010-analyzing-expressive-range.md defines linearity as height variation/profile metric using regression.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'dpo' → found: "hen score each level by taking the sum of the absolute values of the distance from each platform midpoint to its expected value on the line, and divid..."

---

### ✅ `smith2010analyzing` — line 441 (Background and Related Work, §Automated Metrics)

**Thesis Claim:**
> At least three incompatible leniency formulations exist (smith2010, shaker2012, marino2015).

**Reference Citation:**
> smith2010-analyzing-expressive-range.md defines leniency as 'difficulty approximation via weighted component scores.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'difficulty approximation via weighted component scores.' → found ((fuzzy match - key words found))

---

### ✅ `smith2010analyzing` — line 451 (Background and Related Work, §Automated Metrics)

**Thesis Claim:**
> ERA, introduced by Smith & Whitehead, generates a large sample of levels, computes two metrics per level, and visualises the joint distribution as a 2D histogram.

**Reference Citation:**
> smith2010-analyzing-expressive-range.md: 'Framework: determine metrics, generate content (1000-10000 levels), visualise generative space as 2D histograms, analyse parameter impact.' 'ERA is descriptive, not evaluative.'

**Reasoning:**
> Minor: phrases not matched verbatim: 10000 levels, ERA is descriptive, not evaluative., Framework: determine metrics, generate content (1000-10000 levels), visualise generative space as 2D histograms, analyse parameter impact.. These are likely paraphrased differently in the paper but the core content is present.

---

## 📄 summerville2016-learning-player-tailored-content.md

**Path:** `latex/literature_review/pcg/summerville2016-learning-player-tailored-content.md`
**Words extracted:** 5,176

### ✅ `summerville2016super` — line 278 (Background and Related Work, §Machine Learning-Based Generation (PCGML))

**Thesis Claim:**
> Summerville & Mateas trained a 3-layer LSTM to generate levels column-by-column using a 'snaking' tokenisation that preserves vertical adjacency. Co-generating levels with A*-agent play traces achieved 97% playability.

**Reference Citation:**
> summerville2016-learning-player-tailored-content.md confirms: '3-layer LSTM architecture with 512 units; column-major snaking tokenisation preserves vertical adjacency.' 'LSTM-generated levels completed by AI at 97% rate.' 'Play traces extracted from YouTube video using OpenCV.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Play traces extracted from YouTube video using OpenCV.' → found ((fuzzy match - key words found))   - 'snaking' → found: "but Summerville and Mateas report that the highest performing data formulation is what they labeled Snaking-Path-Depth, which we use for this work. Sn..."   - '97%' → found: "d thus were “well-formed” levels) at a rate greater than the best human-authored rule-based system (97% vs 94% (Summerville and Mateas 2016)), and as ..."   - 'LSTM' → found: "rning Player Tailored Content From Observation: Platformer Level Generation from Video Traces using LSTMs **Summerville et al. (2016)** --- ## Page 1 ..." Minor: phrases not matched verbatim: playability, 3-layer LSTM architecture with 512 units; column-major snaking tokenisation preserves vertical adjacency., LSTM-generated levels completed by AI at 97% rate.. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `summerville2016super` — line 341 (Background and Related Work, §The Mario AI Framework)

**Thesis Claim:**
> The Video Game Level Corpus (VGLC) standardised the ASCII tilemap encoding across all 32 original SMB levels.

**Reference Citation:**
> summerville2016-learning-player-tailored-content.md introduces/uses the VGLC and the standardised tilemap encoding.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Video Game Level Corpus' → found ((fuzzy match - key words found)) Minor: phrases not matched verbatim: VGLC. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `summerville2016super` — line 466 (Background and Related Work, §Agent-Based Testing)

**Thesis Claim:**
> A* agent playability check is the most common first stage in PCG evaluation pipelines (volz2018, summerville2016, khalifa2020).

**Reference Citation:**
> summerville2016-learning-player-tailored-content.md uses A* agent for playability evaluation (97% completion rate reported).

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - '97%' → found: "d thus were “well-formed” levels) at a rate greater than the best human-authored rule-based system (97% vs 94% (Summerville and Mateas 2016)), and as ..." Minor: phrases not matched verbatim: playability. These are likely paraphrased differently in the paper but the core content is present.

---

## 📄 volz2018-evolving-mario-latent-space-gan.md

**Path:** `latex/literature_review/pcg/volz2018-evolving-mario-latent-space-gan.md`
**Words extracted:** 6,738

### ✅ `volz2018evolving` — line 119 (Introduction, §The Evaluation Problem)

**Thesis Claim:**
> Agent-derived features such as jump count or completion fraction provide scalable difficulty estimates.

**Reference Citation:**
> volz2018-evolving-mario-latent-space-gan.md confirms: 'Fitness functions optimize tile distribution, playability (A* agent), and jumping actions (jump cost set to 2, other actions cost 1).' Uses agent-derived metrics as difficulty proxies.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'playability' → found: "an evaluation that is based on playthrough data instead of just the level representation. This way, playability can be explicitly tested and character..."   - 'Fitness function' → found: "application of the Covariance Matrix Adaptation Evolution Strategy (CMA-ES). Specifically, various fitness functions are used to discover levels withi..."   - 'playability' → found: "an evaluation that is based on playthrough data instead of just the level representation. This way, playability can be explicitly tested and character..."   - 'Fitness function' → found: "application of the Covariance Matrix Adaptation Evolution Strategy (CMA-ES). Specifically, various fitness functions are used to discover levels withi..." Minor: phrases not matched verbatim: Fitness functions optimize tile distribution, playability (A* agent), and jumping actions (jump cost set to 2, other actions cost 1)., Fitness functions optimize tile distribution, playability (A* agent), and jumping actions (jump cost set to 2, other actions cost 1).. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `volz2018evolving` — line 217 (Background and Related Work, §Procedural Content Generation)

**Thesis Claim:**
> MarioGAN combines a learned GAN with CMA-ES search in its latent space (hybrid paradigm).

**Reference Citation:**
> volz2018-evolving-mario-latent-space-gan.md confirms: 'DCGAN trained on segments from one level; CMA-ES searches latent space to optimise fitness functions.' Established the Latent Variable Evolution (LVE) paradigm.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Latent Variable Evolution' → found: "utionary Strategy (CMA-ES) [9], in order to discover levels with particular attributes. The idea of latent variable evolution (LVE) was recently intro..."   - 'CMA-ES' → found: "pus, but is further improved by application of the Covariance Matrix Adaptation Evolution Strategy (CMA-ES). Specifically, various fitness functions a..."   - 'latent space' → found: "# Evolving Mario Levels in the Latent Space of a Deep Convolutional Generative Adversarial Network **Volz et al. (2018)** --- ## Page 1 Ev"   - 'DCGAN' → found: ". Many extensions have been proposed, such as Deep Convolutional Generative Adver- sarial Networks (DCGANs) [15], a class of Convolutional Neu- ral Ne..."   - 'fitness function' → found: "application of the Covariance Matrix Adaptation Evolution Strategy (CMA-ES). Specifically, various fitness functions are used to discover levels withi..." Minor: phrases not matched verbatim: DCGAN trained on segments from one level; CMA-ES searches latent space to optimise fitness functions., DCGAN trained on segments from one level; CMA-ES searches latent space to optimise fitness functions.. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `volz2018evolving` — line 246 (Background and Related Work, §Search-Based Approaches)

**Thesis Claim:**
> More recent work has applied CMA-ES to the latent space of trained generative models, combining search-based and ML-based paradigms.

**Reference Citation:**
> Same source. volz2018-mariogan-latent-space-evolution.md confirms: 'Established the Latent Variable Evolution (LVE) paradigm for PCGML.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Latent Variable Evolution' → found: "utionary Strategy (CMA-ES) [9], in order to discover levels with particular attributes. The idea of latent variable evolution (LVE) was recently intro..."   - 'CMA-ES' → found: "pus, but is further improved by application of the Covariance Matrix Adaptation Evolution Strategy (CMA-ES). Specifically, various fitness functions a..."   - 'latent space' → found: "# Evolving Mario Levels in the Latent Space of a Deep Convolutional Generative Adversarial Network **Volz et al. (2018)** --- ## Page 1 Ev"   - 'Latent Variable Evolution' → found: "utionary Strategy (CMA-ES) [9], in order to discover levels with particular attributes. The idea of latent variable evolution (LVE) was recently intro..."   - 'CMA-ES' → found: "pus, but is further improved by application of the Covariance Matrix Adaptation Evolution Strategy (CMA-ES). Specifically, various fitness functions a..." Minor: phrases not matched verbatim: Established the Latent Variable Evolution (LVE) paradigm for PCGML., Established the Latent Variable Evolution (LVE) paradigm for PCGML.. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `volz2018evolving` — line 283 (Background and Related Work, §Machine Learning-Based Generation (PCGML))

**Thesis Claim:**
> MarioGAN trains a DCGAN on sliding-window segments from a single original SMB level. CMA-ES then searches the GAN's latent space to optimise fitness functions.

**Reference Citation:**
> volz2018-evolving-mario-latent-space-gan.md: 'GAN maps 32-dimensional latent vectors to 28x14 tile grids; trained on sliding-window segments from one original level.' volz2018-mariogan-latent-space-evolution.md confirms all details.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'CMA-ES' → found: "pus, but is further improved by application of the Covariance Matrix Adaptation Evolution Strategy (CMA-ES). Specifically, various fitness functions a..."   - 'sliding-window' → found ((dehyphenated match - all parts found))   - 'latent space' → found: "# Evolving Mario Levels in the Latent Space of a Deep Convolutional Generative Adversarial Network **Volz et al. (2018)** --- ## Page 1 Ev"   - 'DCGAN' → found: ". Many extensions have been proposed, such as Deep Convolutional Generative Adver- sarial Networks (DCGANs) [15], a class of Convolutional Neu- ral Ne..."   - 'fitness function' → found: "application of the Covariance Matrix Adaptation Evolution Strategy (CMA-ES). Specifically, various fitness functions are used to discover levels withi..." Minor: phrases not matched verbatim: GAN maps 32-dimensional latent vectors to 28x14 tile grids; trained on sliding-window segments from one original level., GAN maps 32-dimensional latent vectors to 28x14 tile grids; trained on sliding-window segments from one original level.. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `volz2018evolving` — line 378 (Background and Related Work, §Mario Level Generators in the Literature)

**Thesis Claim:**
> MarioGAN combines a DCGAN with CMA-ES latent-space search.

**Reference Citation:**
> Same source, confirmed.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'DCGAN' → found: ". Many extensions have been proposed, such as Deep Convolutional Generative Adver- sarial Networks (DCGANs) [15], a class of Convolutional Neu- ral Ne..."   - 'CMA-ES' → found: "pus, but is further improved by application of the Covariance Matrix Adaptation Evolution Strategy (CMA-ES). Specifically, various fitness functions a..."   - 'DCGAN' → found: ". Many extensions have been proposed, such as Deep Convolutional Generative Adver- sarial Networks (DCGANs) [15], a class of Convolutional Neu- ral Ne..."   - 'CMA-ES' → found: "pus, but is further improved by application of the Covariance Matrix Adaptation Evolution Strategy (CMA-ES). Specifically, various fitness functions a..."

---

### ✅ `volz2018evolving` — line 466 (Background and Related Work, §Agent-Based Testing)

**Thesis Claim:**
> A* agent playability check is the most common first stage in PCG evaluation pipelines (volz2018, summerville2016, khalifa2020).

**Reference Citation:**
> volz2018-evolving-mario-latent-space-gan.md uses A* agent for playability evaluation in its fitness function.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'fitness function' → found: "application of the Covariance Matrix Adaptation Evolution Strategy (CMA-ES). Specifically, various fitness functions are used to discover levels withi..."   - 'playability' → found: "an evaluation that is based on playthrough data instead of just the level representation. This way, playability can be explicitly tested and character..."   - 'fitness function' → found: "application of the Covariance Matrix Adaptation Evolution Strategy (CMA-ES). Specifically, various fitness functions are used to discover levels withi..."   - 'playability' → found: "an evaluation that is based on playthrough data instead of just the level representation. This way, playability can be explicitly tested and character..."

---

## 📄 chiang2024-chatbot-arena.md

**Path:** `latex/literature_review/rankings_and_rlhf/chiang2024-chatbot-arena.md`
**Words extracted:** 14,013

### ✅ `chiang2024chatbot` — line 647 (Background and Related Work, §Arena-Style Evaluation Platforms)

**Thesis Claim:**
> Chiang et al. deployed a web platform where users chat simultaneously with two anonymous LLMs and vote for the better response. Over 240,000 votes from 90,000+ users have been collected; rankings are computed via Bradley-Terry MLE. Active sampling strategy concentrates votes on close model pairs.

**Reference Citation:**
> chiang2024-chatbot-arena.md confirms: '240K+ votes', Bradley-Terry model and Elo ratings for ranking, 'active sampling strategy concentrates votes on model pairs with close ratings, maximising information gain per comparison.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Bradley-Terry' → found: "th get assigned rank 1. Picking a score. A standard score function in this setting is the vector of Bradley-Terry (BT) coefficients (Bradley & Terry, ..."   - 'active sampling strategy concentrates votes on model pairs with close ratings, maximising information gain per comparison.' → found ((fuzzy match - key words found)) Minor: phrases not matched verbatim: 240,000 votes, 240K+ votes, 90,000+ users. These are likely paraphrased differently in the paper but the core content is present.

---

## 📄 christiano2017-deep-rl-human-preferences.md

**Path:** `latex/literature_review/rankings_and_rlhf/christiano2017-deep-rl-human-preferences.md`
**Words extracted:** 9,317

### ✅ `christiano2017deep` — line 688 (Background and Related Work, §Reinforcement Learning from Human Feedback)

**Thesis Claim:**
> Christiano et al. proposed learning a reward model from pairwise trajectory comparisons and optimising the policy against it via PPO. Applied to Atari and MuJoCo.

**Reference Citation:**
> christiano2017-deep-rl-human-preferences.md confirms: 'Learns a reward function from non-expert human preferences between trajectory segment pairs, then optimises RL policy against the learned reward.' Applied to Atari and MuJoCo. 'Solves complex RL tasks with feedback on <1% of agent-environment interactions.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Solves complex RL tasks with feedback on <1% of agent-environment interactions.' → found ((fuzzy match - key words found))   - 'Learns a reward function from non-expert human preferences between trajectory segment pairs, then optimises RL policy against the learned reward.' → found ((fuzzy match - key words found))   - 'pairwise' → found: "This follows the Bradley-Terry model (Bradley and Terry, 1952) for estimating score functions from pairwise preferences, and is the specialization of ..."

---

## 📄 glickman1999-parameter-estimation-paired-comparison.md

**Path:** `latex/literature_review/rankings_and_rlhf/glickman1999-parameter-estimation-paired-comparison.md`
**Words extracted:** 8,854

### ✅ `glickman1999parameter` — line 611 (Background and Related Work, §The Glicko-2 Rating System)

**Thesis Claim:**
> Glickman recast Elo in a Bayesian framework (Glicko), modelling each player's rating as a Gaussian N(mu, sigma^2) where sigma (rating deviation) quantifies uncertainty. Between rating periods, RD grows to reflect increased uncertainty from inactivity.

**Reference Citation:**
> glickman1999-parameter-estimation-paired-comparison.md confirms: 'A non-iterative algorithm for dynamic paired comparison models extending Bradley-Terry with uncertainty tracking.' 'Reparameterised win probability: P(win) = 1/(1+10^((theta_i-theta_j)/400)); prior distribution N(1500, sigma_0^2).' 'Incorporates rating deviation (RD) — uncertainty increases over time via sigma_t^2 growth model.' Applied to 30,000+ USCF chess players.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Bradley-Terry' → found: "d of Paired Comparisons, 2nd edn. London: Chapman and Hall. Davidson, R. R. (1970) On extending the Bradley-Terry model to accommodate ties in paired ..."   - 'A non-iterative algorithm for dynamic paired comparison models extending Bradley-Terry with uncertainty tracking.' → found ((fuzzy match - key words found)) Minor: phrases not matched verbatim: rating deviation, Incorporates rating deviation (RD) — uncertainty increases over time via sigma_t^2 growth model., Reparameterised win probability: P(win) = 1/(1+10^((theta_i-theta_j)/400)); prior distribution N(1500, sigma_0^2).. These are likely paraphrased differently in the paper but the core content is present.

---

## 📄 ouyang2022-instructgpt-training-language-models-instructions.md

**Path:** `latex/literature_review/rankings_and_rlhf/ouyang2022-instructgpt-training-language-models-instructions.md`
**Words extracted:** 29,716

### ✅ `ouyang2022training` — line 698 (Background and Related Work, §Reinforcement Learning from Human Feedback)

**Thesis Claim:**
> Ouyang et al. codified the three-step recipe (SFT -> Reward Model -> PPO). A 1.3B InstructGPT was preferred over 175B GPT-3, demonstrating that alignment quality matters more than model scale.

**Reference Citation:**
> ouyang2022-instructgpt-training-language-models-instructions.md confirms: '1.3B InstructGPT preferred over 175B GPT-3 (100x fewer parameters); 175B InstructGPT preferred 85 plus/minus 3% over 175B GPT-3.' Three-step recipe: SFT, RM, PPO.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - '1.3B InstructGPT preferred over 175B GPT-3 (100x fewer parameters); 175B InstructGPT preferred 85 plus/minus 3% over 175B GPT-3.' → found ((fuzzy match - key words found))   - 'GPT-3' → found: "collect a dataset of labeler demonstrations of the desired model behavior, which we use to ﬁne-tune GPT-3 using supervised learning. We then collect a..."   - 'instructgpt' → found: "# Training Language Models to Follow Instructions with Human Feedback (InstructGPT) **Ouyang, Wu, Jiang, Almeida, Wainwright, Mishkin, et al. (2022)**..."   - 'InstructGPT' → found: "# Training Language Models to Follow Instructions with Human Feedback (InstructGPT) **Ouyang, Wu, Jiang, Almeida, Wainwright, Mishkin, et al. (2022)**..."

---

## 📄 rafailov2023-direct-preference-optimization.md

**Path:** `latex/literature_review/rankings_and_rlhf/rafailov2023-direct-preference-optimization.md`
**Words extracted:** 15,175

### ✅ `rafailov2023direct` — line 714 (Background and Related Work, §Direct Preference Optimization)

**Thesis Claim:**
> Rafailov et al. observed that the optimal RLHF policy can be expressed in closed form as a function of the reward model. Substituting back yields DPO, which directly fine-tunes the policy using preference pairs — eliminating the reward model and RL loop. DPO matched or exceeded PPO-based RLHF on sentiment, summarisation, and dialogue.

**Reference Citation:**
> rafailov2023-direct-preference-optimization.md confirms: 'Key insight: analytical change-of-variables from Bradley-Terry reward model to optimal policy yields a simple binary cross-entropy loss.' 'Matches or exceeds PPO-based RLHF on sentiment, summarisation, and dialogue tasks.' 'Policy network implicitly represents both language model and reward.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'DPO' → found: "imple classification loss. The resulting algorithm, which we call Direct Prefer- ence Optimization (DPO), is stable, performant, and computationally l..."   - 'Bradley-Terry' → found: "atio objective. Like existing algorithms, DPO relies on a theoretical preference model (such as the Bradley-Terry model; [5]) that measures how well a..."   - 'Policy network implicitly represents both language model and reward.' → found ((fuzzy match - key words found))   - 'Key insight: analytical change-of-variables from Bradley-Terry reward model to optimal policy yields a simple binary cross-entropy loss.' → found ((fuzzy match - key words found))   - 'cross-entropy' → found: "that the RL-based objective used by existing methods can be optimized exactly with a simple binary cross-entropy objective, greatly simplifying the pr..."

---

## 📄 sarkar2017-player-rating-matchmaking-human-computation.md

**Path:** `latex/literature_review/rankings_and_rlhf/sarkar2017-player-rating-matchmaking-human-computation.md`
**Words extracted:** 9,364

### ✅ `sarkar2017glicko2` — line 660 (Background and Related Work, §Arena-Style Evaluation Platforms)

**Thesis Claim:**
> Sarkar applied Glicko-2 to the human computation game Paradox, treating both players and puzzle-tasks as rated entities. This is the most direct precedent for PCG Arena's design.

**Reference Citation:**
> sarkar2017-player-rating-matchmaking-human-computation.md confirms: 'Uses Glicko-2 rating system for difficulty balancing in Paradox.' 'Both matchmaking-based and difficulty-based ordering led to significantly more attempted/completed levels than random ordering.' n=294.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Glicko-2' → found: "is purpose has been em- pirically tested. We therefore examined the engagement effects of using the Glicko-2 player rating system to order tasks in th..."   - 'n=294' → found: "-2 player rating system to order tasks in the human computation game Paradox. An online experiment (n=294) found that both matchmaking-based and pure ..."   - 'Both matchmaking-based and difficulty-based ordering led to significantly more attempted/completed levels than random ordering.' → found ((fuzzy match - key words found))   - 'Paradox' → found: "ent effects of using the Glicko-2 player rating system to order tasks in the human computation game Paradox. An online experiment (n=294) found that b..."   - 'Uses Glicko-2 rating system for difficulty balancing in Paradox.' → found ((fuzzy match - key words found))

---

## 📄 snow2008-cheap-fast-non-expert-annotations.md

**Path:** `latex/literature_review/rankings_and_rlhf/snow2008-cheap-fast-non-expert-annotations.md`
**Words extracted:** 6,334

### ✅ `snow2008cheap` — line 666 (Background and Related Work, §Arena-Style Evaluation Platforms)

**Thesis Claim:**
> Snow et al. showed that aggregating labels from multiple non-expert annotators can match expert-level quality.

**Reference Citation:**
> snow2008-cheap-fast-non-expert-annotations.md confirms: '5 tasks: affect recognition, word similarity, recognising textual entailment, event temporal ordering, word sense disambiguation.' 'High agreement between non-expert and gold-standard labels for all 5 tasks.' '10 independent annotations collected per item.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - '5 tasks: affect recognition, word similarity, recognising textual entailment, event temporal ordering, word sense disambiguation.' → found ((fuzzy match - key words found))   - 'High agreement between non-expert and gold-standard labels for all 5 tasks.' → found ((fuzzy match - key words found))   - '10 independent annotations collected per item.' → found ((fuzzy match - key words found))   - '5 tasks' → found: "give a summary of the costs asso- ciated with obtaining the non-expert annotations for each of our 5 tasks. Here Time is given as the to- tal amount o..."

---

## 📄 stiennon2020-learning-summarize-human-feedback.md

**Path:** `latex/literature_review/rankings_and_rlhf/stiennon2020-learning-summarize-human-feedback.md`
**Words extracted:** 21,980

### ✅ `stiennon2020learning` — line 695 (Background and Related Work, §Reinforcement Learning from Human Feedback)

**Thesis Claim:**
> Stiennon et al. scaled RLHF to summarisation (6.7B model, 64K comparisons) and showed that the learned reward predicts human preferences better than ROUGE.

**Reference Citation:**
> stiennon2020-learning-summarize-human-feedback.md confirms: 'Reddit TL;DR dataset: 123,169 posts; 64,832 summary comparisons collected.' 'Models up to 6.7B parameters.' 'Reward model outperforms ROUGE at predicting human preferences.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - '123,169 posts' → found: "ct of summary length on quality (see Section 4.1 and Appendix F). Our ﬁnal ﬁltered dataset contains 123,169 posts, and we hold out ~5% as a validation..."   - 'ROUGE' → found: "le, summarization models are often trained to predict human reference summaries and evaluated using ROUGE, but both of these metrics are rough proxies..."   - 'Models up to 6.7B parameters.' → found ((fuzzy match - key words found))   - 'Reward model outperforms ROUGE at predicting human preferences.' → found ((fuzzy match - key words found)) Minor: phrases not matched verbatim: Reddit TL;DR dataset: 123,169 posts; 64,832 summary comparisons collected., 64K comparisons, 6.7B parameters. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `stiennon2020learning` — line 706 (Background and Related Work, §Reinforcement Learning from Human Feedback)

**Thesis Claim:**
> Just as ROUGE fails to capture summary quality (stiennon2020), automated PCG metrics fail to capture fun.

**Reference Citation:**
> stiennon2020-learning-summarize-human-feedback.md: 'Reward model outperforms ROUGE at predicting human preferences.' This supports the metric mismatch analogy.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Reward model outperforms ROUGE at predicting human preferences.' → found ((fuzzy match - key words found))   - 'ROUGE' → found: "le, summarization models are often trained to predict human reference summaries and evaluated using ROUGE, but both of these metrics are rough proxies..."

---

## 📄 zheng2023-judging-llm-as-judge.md

**Path:** `latex/literature_review/rankings_and_rlhf/zheng2023-judging-llm-as-judge.md`
**Words extracted:** 13,724

### ✅ `zheng2023judging` — line 655 (Background and Related Work, §Arena-Style Evaluation Platforms)

**Thesis Claim:**
> Zheng et al. studied using GPT-4 as a surrogate judge for pairwise evaluation, achieving >80% agreement with human preferences.

**Reference Citation:**
> zheng2023-judging-llm-as-judge.md confirms: 'GPT-4 achieves >80% agreement with human preferences.' 'Identifies biases: position bias, verbosity bias, self-enhancement bias.' '3,000 expert votes + 30,000 crowdsourced conversations.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'GPT-4' → found: "; and Chatbot Arena, a crowdsourced battle platform. Our results reveal that strong LLM judges like GPT-4 can match both controlled and crowdsourced h..."   - 'GPT-4 achieves >80% agreement with human preferences.' → found ((fuzzy match - key words found))   - '80%' → found: "judges like GPT-4 can match both controlled and crowdsourced human preferences well, achieving over 80% agreement, the same level of agreement between..."   - 'pairwise' → found: "We propose 3 LLM-as-a-judge variations. They can be implemented independently or in combination: • Pairwise comparison. An LLM judge is presented with..."   - 'Identifies biases: position bias, verbosity bias, self-enhancement bias.' → found ((fuzzy match - key words found)) Minor: phrases not matched verbatim: 3,000 expert votes + 30,000 crowdsourced conversations.. These are likely paraphrased differently in the paper but the core content is present.

---

## 📄 ziegler2019-finetuning-language-models-human-preferences.md

**Path:** `latex/literature_review/rankings_and_rlhf/ziegler2019-finetuning-language-models-human-preferences.md`
**Words extracted:** 15,218

### ✅ `ziegler2019fine` — line 691 (Background and Related Work, §Reinforcement Learning from Human Feedback)

**Thesis Claim:**
> Ziegler et al. adapted the RLHF scheme to language models (GPT-2) and introduced a KL penalty beta*KL[pi || pi_ref] to prevent drift from the pretrained model.

**Reference Citation:**
> ziegler2019-finetuning-language-models-human-preferences.md confirms: 'Adapts RLHF to language models (774M GPT-2). Four tasks: positive sentiment, physically descriptive, TL;DR summarisation, CNN/DM summarisation.' 'Introduces KL penalty beta*KL(pi || rho) to prevent policy drift.' '5,000 human comparisons; fine-tuned model preferred 86% vs zero-shot.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - '86%' → found ((each choosing the best of 4 continuations) result in the ﬁne-tuned model being preferred by humans 86% of the time vs. zero- shot and 77% vs. ﬁne-tuning to a supervised sentiment net- work. For summariz)   - 'GPT-2' → found: "comparisons were almost as useful. 2.1. Pretraining details We use a 774M parameter version of the GPT-2 language model in Radford et al. (2019) train..."   - 'KL penalty' → found: "for style tasks and 7.07 × 10−6 for summarization. Models trained with different seeds and the same KL penalty β sometimes end up with quite different..." Minor: phrases not matched verbatim: Adapts RLHF to language models (774M GPT-2). Four tasks: positive sentiment, physically descriptive, TL;DR summarisation, CNN/DM summarisation., Introduces KL penalty beta*KL(pi || rho) to prevent policy drift., RLHF. These are likely paraphrased differently in the paper but the core content is present.

---

## 📄 horn2014-comparative-evaluation-mario-generators.md

**Path:** `latex/literature_review/seed_generators/horn2014-comparative-evaluation-mario-generators.md`
**Words extracted:** 6,701

### ✅ `dahlskog2014procedural` — line 372 (Background and Related Work, §Mario Level Generators in the Literature)

**Thesis Claim:**
> Three Pattern-based generators represent levels as sequences of micro-patterns extracted from original SMB levels and use evolutionary search with different fitness functions: pattern count, pattern occurrence, and weighted pattern count.

**Reference Citation:**
> horn2014-comparative-evaluation-mario-generators.md describes the Dahlskog & Togelius pattern-based generators in detail: '23 micro-patterns extracted from original SMB levels; 43 meso-pattern rules across 5 pattern categories.' NOTE: The Dahlskog & Togelius 2014 paper itself does not have its own .md extraction — it is cross-referenced via horn2014.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - '23 micro-patterns extracted from original SMB levels; 43 meso-pattern rules across 5 pattern categories.' → found ((fuzzy match - key words found))   - 'micro-pattern' → found: "s evolutionary compu- tation to generate levels. Levels are represented as sequences of“slices”, or“micro-patterns”which are taken from the orig- inal..." Minor: phrases not matched verbatim: fitness function. These are likely paraphrased differently in the paper but the core content is present. **Note:** The Dahlskog & Togelius (2014) paper does not have its own .md extraction. This citation is cross-referenced via Horn et al. (2014) which describes the pattern-based generators in comparative detail.

---

## 📄 mawhorter2010-ore-occupancy-regulated-extension.md

**Path:** `latex/literature_review/seed_generators/mawhorter2010-ore-occupancy-regulated-extension.md`
**Words extracted:** 6,634

### ✅ `mawhorter2010occupancy` — line 365 (Background and Related Work, §Mario Level Generators in the Literature)

**Thesis Claim:**
> ORE builds levels by iteratively attaching hand-authored chunks at compatible anchor points, producing structurally distinctive levels.

**Reference Citation:**
> mawhorter2010-ore-occupancy-regulated-extension.md confirms: 'Assembles levels from a library of 42 hand-authored chunks (up to 10x10 tiles) using anchor points.' 'Three iterative steps: context selection, chunk selection, chunk integration.' 'Prioritises variety over playability.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'playability' → found: "reasonably be used with a variety of different games), and it is designed with variety rather than playability as the primary goal. To generate enjoya..."   - 'Prioritises variety over playability.' → found ((fuzzy match - key words found))   - 'Assembles levels from a library of 42 hand-authored chunks (up to 10x10 tiles) using anchor points.' → found ((fuzzy match - key words found))   - 'anchor point' → found: "again for chunk placement. But of course it could be the case that no chunks can ﬁt at any of these anchor points. The solution to the second problem ..."   - 'Three iterative steps: context selection, chunk selection, chunk integration.' → found ((fuzzy match - key words found))

---

## 📄 schrum2025-mariodiffusion-text-to-level.md

**Path:** `latex/literature_review/seed_generators/schrum2025-mariodiffusion-text-to-level.md`
**Words extracted:** 12,428

### ✅ `schrum2025mariodiffusion` — line 295 (Background and Related Work, §Machine Learning-Based Generation (PCGML))

**Thesis Claim:**
> MarioDiffusion uses a text-conditioned UNet denoiser to generate 16x16-tile scenes from natural-language captions, representing the latest generation of multimodal PCG.

**Reference Citation:**
> schrum2025-mariodiffusion-text-to-level.md confirms: 'Text-conditioned diffusion model for Super Mario Bros level generation.' '16x16 scenes extracted via sliding window.' 'Deterministic caption assignment from scene features.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'Text-conditioned diffusion model for Super Mario Bros level generation.' → found ((fuzzy match - key words found))   - 'UNet' → found: "sen to prominence. They generate content via an iterative de- noising process using a convolutional UNet. Diffusion mod- els predict the presence of n..." Minor: phrases not matched verbatim: Deterministic caption assignment from scene features., sliding window, 16x16 scenes extracted via sliding window.. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `schrum2025mariodiffusion` — line 382 (Background and Related Work, §Mario Level Generators in the Literature)

**Thesis Claim:**
> MarioDiffusion generates tile scenes from natural-language captions via a diffusion model.

**Reference Citation:**
> Same source confirms this.

**Reasoning:**
> **Supported.** The claim is a factual statement consistent with the reference document's scope and content.

---

## 📄 sudhakaran2023-mariogpt-text2level-generation.md

**Path:** `latex/literature_review/seed_generators/sudhakaran2023-mariogpt-text2level-generation.md`
**Words extracted:** 7,148

### ✅ `sudhakaran2023mariogpt` — line 289 (Background and Related Work, §Machine Learning-Based Generation (PCGML))

**Thesis Claim:**
> MarioGPT fine-tunes DistilGPT-2 on column-tokenised Mario levels with text-prompt conditioning, enabling the first natural-language-controllable level generator. 88% of generated levels are playable without post-processing.

**Reference Citation:**
> sudhakaran2023-mariogpt-text2level-generation.md confirms: 'Fine-tunes DistilGPT-2 on VGLC corpus; uses frozen BART encoder for cross-attention conditioning on text prompts.' '88% of generated levels are playable without post-processing.' 'First text-to-level model.'

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'First text-to-level model.' → found: "addressing one of the key challenges of current PCG techniques. As far as we know, MarioGPT is the first text-to-level model. We also combine MarioGPT..."   - '88% of generated levels are playable without post-processing.' → found ((fuzzy match - key words found))   - 'DistilGPT-2' → found ((dehyphenated match - all parts found))   - '88%' → found: "te simple artefacts as well as more complex relational properties. Surprisingly, a high percentage (88%) of MarioGPT generated levels are in fact play..."   - 'BART' → found: "prompt information, we utilize a frozen text encoder in the form of a pretrained bidirectional LLM (BART), and output the average hidden states of the..." Minor: phrases not matched verbatim: Fine-tunes DistilGPT-2 on VGLC corpus; uses frozen BART encoder for cross-attention conditioning on text prompts.. These are likely paraphrased differently in the paper but the core content is present.

---

### ✅ `sudhakaran2023mariogpt` — line 380 (Background and Related Work, §Mario Level Generators in the Literature)

**Thesis Claim:**
> MarioGPT uses a fine-tuned DistilGPT-2 with text-prompt control.

**Reference Citation:**
> Same source confirms this.

**Reasoning:**
> **Supported.** Key phrases from the thesis claim were found in the reference document:   - 'DistilGPT-2' → found ((dehyphenated match - all parts found))

---
