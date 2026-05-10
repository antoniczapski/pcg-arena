# EDA and User Study Replanning

Date: 2026-05-10
Input files reviewed:

- `eda/data.md`
- `latex/main_report/main_report.tex`, especially the current `Results and Discussion` section
- Fresh export directory: `eda/data_10_05_2026/`

This document is a planning document only. It proposes a new strategy for the EDA / user-study chapter before rewriting the thesis/report text or regenerating all plots.

---

## 0. Main diagnosis

The current EDA chapter reads like a sequence of hypothesis tests, many of which are either inconclusive or based on weak / inappropriate proxies. The result is boring because the reader repeatedly sees: hypothesis, statistical test, weak effect, not supported / partially supported.

The stronger story is not: “we tried many hypotheses and most failed.”

The stronger story should be:

> PCG Arena collected blind pairwise human preferences, tags, gameplay telemetry, and trajectories. These data let us compare generators not only by win rate, but also by their structural expressive range, gameplay footprint, failure modes, and user preference diversity.

So the chapter should become a research-oriented characterization of the platform data:

1. What was collected and how reliable is it?
2. Which generators do humans prefer?
3. How do generators differ structurally?
4. How do players actually move through levels from each generator?
5. Are there visible groups of users / play styles / preference modes?
6. What do tags add beyond votes?
7. What does the platform enable as a research instrument?

Statistical tests should be used sparingly. The chapter should prioritize clear figures, tables, visual comparisons, effect sizes, and careful interpretation.

---

## 1. Immediate factual corrections

### 1.1 Recruitment description

Current/previous wording mentioning a “dedicated university-hosted event” should be removed.

Use:

> Participants were recruited through university social-media channels, word of mouth among game-development and computer-science communities, and a small promoted Reddit campaign targeting game-development / procedural-generation communities.

Add if useful:

> The Reddit promotion budget was approximately USD 20.

Do not claim a university event.

### 1.2 Participant identity and session continuity

Do not write that an optional account link was used to track session continuity.

Better wording:

> Participation was anonymous. The platform assigned browser-based anonymous player identifiers and session identifiers, persisted through cookies/local browser storage. Therefore, “players” in the analysis are best interpreted as anonymous browser/player IDs rather than verified unique humans. Clearing cookies or changing device/browser could create a new ID.

Current fresh-data sanity check:

- Player profiles in export: 79
- Unique players appearing in first 1000 exported votes: 77
- Sessions appearing in first 1000 exported votes: 213
- Linked user accounts: 0

So we can discuss anonymous player IDs and sessions, but not demographic participants.

### 1.3 Death count / difficulty

The old “number of deaths” wording is misleading. The platform currently gives each side one attempt. A player can therefore die at most once per level side.

Use:

- `death indicator`
- `death/failure rate`
- `one-attempt failure rate`
- `death location`, where available

Avoid:

- “average number of deaths” as if players can repeatedly retry the same level
- flow-channel arguments based on repeated deaths
- claims like “levels with 3 deaths per play”

Fresh-data sanity check from the first 1000 votes:

- 2000 telemetry side records
- 1968 played side records
- 1968 non-empty trajectories embedded in vote telemetry
- deaths are always 0 or 1
- max deaths = 1
- death-location count is 0 or 1

`avg_deaths` in `level_stats` should be interpreted as death rate, not average repeated deaths.

### 1.4 Trajectory availability

Do not write that trajectory data was stored only for a small subset in a way that sounds like an intentional sample.

Better wording:

> Trajectory recording was added after the earliest stage of deployment. From that point onward, gameplay telemetry includes sampled Mario positions `(tick, x, y, state)`. The standalone trajectory export is currently paginated/truncated, but the vote export also contains per-side trajectory arrays for recorded plays.

Important distinction:

- `pcg-arena-trajectories-2026-05-10.json` contains only 100 of 2429 trajectories because of `limit=100`.
- `pcg-arena-votes-2026-05-10.json` contains 1000 votes and 2000 side-level telemetry records, with 1968 non-empty trajectories.

For trajectory plots we should use telemetry embedded in votes, and later fetch the remaining votes / trajectory pages.

### 1.5 Sessions-per-player plot

If the sessions-per-player plot is only one column, remove it. It does not help the reader.

Better options:

- Votes per anonymous player ID, log-scale histogram.
- Cumulative contribution curve / Lorenz curve: what fraction of votes comes from top 1, 5, 10 players?
- Sessions per active player only if computed from actual vote `session_id`s and it shows variation.
- A table: total anonymous player IDs, active voters, sessions, median votes per player, top-player vote share.

### 1.6 Confusion matrix color caption

Fix wording:

> Lighter green indicates higher win rates for the row generator.

Not darker green.

### 1.7 Remove / avoid “flow channel” section

The current RQ1/H1 is not a good fit for this platform.

Reasons:

- One-shot battle design means failure/death is a binary event, not a repeated-death difficulty measure.
- The vote is collected after comparing two levels under a short one-attempt protocol.
- “Moderate difficulty is optimal” is a broad psychology/game-design claim; this dataset is not ideal for testing it.
- Even if death/failure correlates with lower preference, that is unsurprising under the one-shot design and not an interesting thesis finding.

Replace it with generator characterization and expressive-range analysis.

---

## 2. Proposed new chapter structure

Working title:

> Exploratory Analysis of Human Preference and Gameplay Telemetry

Alternative title:

> User Study and Generator Characterisation

### Section A — Data collection protocol

Purpose: explain what the platform collected, recruitment, anonymity, and limitations.

Content:

- Blind A/B comparison design.
- Anonymous browser-based player IDs and session IDs.
- Recruitment channels: university social media, word of mouth, promoted Reddit campaign.
- One attempt per level side.
- Optional tags.
- Telemetry: completion, duration, jump count, coins, enemies, death indicator/location, trajectory samples after instrumentation was added.
- Caveat: no demographic survey, anonymous IDs are not guaranteed unique people.

Figures/tables:

- Dataset summary table with fresh numbers.
- Data schema diagram linking players, votes, levels, trajectories, tags.

### Section B — Data coverage and cleaning

Purpose: make the dataset trustworthy before interpreting results.

Fresh known numbers from `data_10_05_2026`:

- 1104 levels in `level_stats`
- 15 generator IDs in `level_stats`, including `mariodpo` and `test-gen`
- 79 anonymous player profiles
- 1192 total votes reported, 1000 currently present in exported file
- 2429 total trajectories reported, 100 currently present in standalone trajectory file
- 2000 per-side telemetry records in the first 1000 vote records
- 1968 non-empty trajectories embedded in vote telemetry

Cleaning rules to state:

- Exclude `test-gen` from research plots unless explicitly labeled as diagnostic/test data.
- Exclude `SKIP` votes from preference ranking but include them in platform/engagement stats.
- Treat ties as 0.5/0.5 for generator ranking.
- Interpret death as binary failure per side.
- Clip or winsorize extreme `duration_seconds` values for plots; the current export has a very large duration outlier, likely from an inactive browser tab.
- Use complete paginated exports before final numbers.

Figures/tables:

- Dataset summary table.
- Vote result distribution.
- Votes over calendar time.
- Engagement concentration curve, not a weak sessions-per-player chart.

### Section C — Generator preference ranking

Research question:

> RQ1: Which generators are preferred by players under blind A/B comparison?

This should be the first “real result” because it is the core purpose of PCG Arena.

Analysis:

- Compute generator scores from pairwise votes:
  - wins = 1
  - ties = 0.5
  - losses = 0
  - skips excluded
- Also compute Elo / Bradley–Terry / Glicko-style rankings from the same vote table.
- Show confidence/uncertainty using bootstrap over votes or player IDs.
- Include pairwise confusion matrix.
- Compare generator families:
  - Original human-authored baseline
  - Neural / ML generators: MarioGPT, MarioGAN, MarioDiffusion, MarioDPO
  - Search / evolutionary generators: genetic, ore, etc.
  - Pattern-based generators: patternCount, patternOccur, patternWeightCount

Preliminary ranking from first 1000 vote records by simple score rate:

| Generator | Score rate |
|---|---:|
| original | 0.833 |
| mariodpo | 0.832 |
| ore | 0.655 |
| mariogpt | 0.643 |
| notch | 0.532 |
| mariogan | 0.506 |
| hopper | 0.490 |
| genetic | 0.490 |
| marioDiffusion | 0.444 |
| patternWeightCount | 0.385 |
| notchParamRand | 0.367 |
| notchParam | 0.307 |
| patternOccur | 0.284 |
| patternCount | 0.262 |

This is already much more interesting than “failed” hypotheses: Original and MarioDPO are almost tied at the top, while pattern-based generators are consistently low.

Figures:

1. Generator leaderboard with uncertainty bars.
2. Pairwise confusion matrix, ordered by ranking.
3. Optional: generator family comparison box/strip plot.

Writing angle:

> The ranking reproduces a meaningful ordering: the human-authored baseline remains strongest, MarioDPO approaches it, and pattern-based generators perform poorly. This validates the platform as a human-preference measurement tool.

### Section D — Static expressive-range analysis

Research question:

> RQ2: Do generators occupy distinct regions of Mario level design space, and do those regions relate to human preference?

This should replace the old “What makes a good generator?” / flow-channel section.

Core idea:

- Compute standard PCG metrics directly from level text files, not from the currently null `level_stats` structural columns.
- Present the generators as design-space distributions.
- Then compare those distributions to human preference rankings.

Metrics to compute:

1. Linearity
   - Use a literature-backed definition.
   - Option A: R² of a linear regression fit to the playable surface / floor profile.
   - Option B: residual variance around the fitted line, where higher means less linear.
   - Be explicit because prior work uses incompatible variants.

2. Leniency
   - Weighted hazard/reward metric.
   - Hazards: gaps, enemies, bullet bills, piranhas, narrow landing areas.
   - Rewards: coins, powerups, safer platforms.
   - Since definitions vary in the literature, define ours as an operational metric and cite the ambiguity.

3. Density
   - Solid-tile density.
   - Enemy density.
   - Reward density.
   - Gap density.

4. Compression distance / diversity
   - Gzip Normalized Compression Distance (NCD).
   - Within-generator diversity: mean pairwise NCD between levels from the same generator.
   - Distance-to-original: mean NCD from generated levels to original levels.

5. Tile / column entropy
   - Character entropy.
   - Unique-column ratio.
   - Compression ratio as repetition proxy.

6. Optional style distance
   - Build a feature vector from static metrics.
   - Compute distance to the `original` generator centroid.
   - Use this descriptively, not as a magic “quality” score.

Figures/tables:

1. Static metrics table per generator:
   - mean ± std for linearity, leniency, density, gap density, enemy density, NCD diversity, distance to original.
2. Expressive Range Analysis plot:
   - 2D histogram or KDE of linearity vs leniency for every generator.
   - Arrange subplots in generator ranking order.
   - This directly addresses the user-requested “expression range analysis” plot.
3. Correlation/association figure:
   - x-axis = generator-level metric, y-axis = generator preference score/Elo.
   - Use labels for generator names.
   - Do not overclaim p-values; with ~14 generators, show direction and effect size.

Implementation notes:

- Existing level files are in `db/seed/levels/<generator>/` for most generators.
- MarioDPO levels appear to be in `MarioDPO/generated_levels_2026_02_01/`; verify how these map to exported `mariodpo::...` level IDs.
- Need to exclude or separately label `test-gen`.
- Backend already contains partial feature extraction in `backend/src/level_features.py`; this can be reused but should be expanded for linearity, compression distance, and expressive-range metrics.

Writing angle:

> Instead of asking whether one hand-picked metric “explains” preference, we characterize each generator’s output distribution. This is closer to expressive-range analysis in PCG literature and more useful to researchers.

### Section E — Gameplay trajectory fingerprints

Research question:

> RQ3: How do players move through levels from different generators, and do preferred generators produce more navigable / varied trajectories?

This is likely the most visually interesting part of the chapter.

Requested figure 1:

> For every generator create one subplot. Concatenate all gameplay trajectories from levels generated by that generator and stack them on top of each other. White background, every trace as a thin red line. Join all subplots into one figure ordered by generator ranking. Each subplot title contains generator name and Elo/rating.

Implementation details:

- Use trajectories embedded in vote telemetry first; they provide far more than the standalone trajectory export.
- For each side telemetry record:
  - generator = left/right generator ID from vote
  - trajectory = telemetry[side].trajectory
  - normalize x/y if necessary to account for different level widths
  - draw x vs y path as thin red line, alpha ~0.03–0.12 depending on count
- Use inverted y-axis if matching screen coordinates.
- Cap extreme trajectories if necessary.

Requested figure 2:

> Same generator grid, but as 2D occupancy histograms / heatmaps.

This is the trajectory expression-range / behavioral footprint plot.

Single-number summaries derived from these plots:

1. Occupancy entropy
   - Convert all trajectory points for a generator into a 2D grid.
   - Compute Shannon entropy of occupied cells.
   - Higher means paths cover more varied space.

2. Occupancy area
   - Fraction of grid cells visited at least once.

3. Path verticality
   - Standard deviation or range of y along trajectories.

4. Path progress
   - Median max x reached normalized by level width.

5. Path diversity
   - Mean pairwise Jaccard distance between trajectories represented as sets of visited grid cells.
   - Simpler alternative: average distance from each trajectory’s occupied-cell vector to the generator centroid.

6. Chokepoint / death concentration
   - Entropy of death x-position bins.
   - Max death-bin share.
   - Early-death rate: death before 25% of level width.

Important interpretation rule:

- Because each level side is one attempt, death metrics are failure-location metrics, not repeated difficulty metrics.

Figures:

1. Stacked red trajectories by generator, ordered by rating.
2. 2D occupancy heatmaps by generator, ordered by rating.
3. Scatter/table: generator rating vs occupancy entropy / progress / verticality / chokepoint concentration.
4. Screenshot placeholder from PCG Arena Detailed Level Statistics page showing trajectories, death histogram, and tags.

Writing angle:

> Trajectory plots make generator differences visible. Some generators produce paths that quickly terminate or concentrate into narrow corridors; stronger generators allow longer, broader, more varied play traces.

This is much more compelling than another weak hypothesis test.

### Section F — User preference heterogeneity

Research question:

> RQ4: Do anonymous players show visibly different preferences or play styles?

This should become a major section, not two short paragraphs.

Goal:

- Show whether users behave like one homogeneous population or whether there are visible subgroups.
- It is acceptable to describe visual structure without claiming statistical proof.

Data representation:

For each anonymous player ID with at least N votes, create a vector:

1. Generator preference vector
   - For each generator, compute average score when this player encountered that generator.
   - If player chooses generator: +1.
   - If player rejects generator: 0.
   - Tie: 0.5.
   - Skip: missing.

2. Playstyle vector
   - median duration
   - completion/failure rate
   - jump count
   - max progress
   - path verticality
   - tag usage rates
   - tie/skip rate

Recommended threshold:

- Use players with ≥5 votes for broad heatmap.
- Use players with ≥10 or ≥15 votes for clustering/embedding.
- Always report how many players remain after filtering.

Figures:

1. User × generator preference heatmap
   - rows = players
   - columns = generators
   - values = preference score
   - cluster rows and columns hierarchically
   - annotate row side bar with vote count

2. 2D embedding of users
   - PCA/UMAP/t-SNE of generator preference vectors or playstyle vectors
   - point size = votes cast
   - color = visually identified cluster or dominant preferred generator family

3. User engagement concentration
   - votes-per-player histogram + cumulative contribution curve
   - show whether data is dominated by a few power users

4. Optional alluvial/sankey-style summary
   - player cluster → preferred generator family → common tags

Possible cautious interpretations:

- “A small group of highly engaged users contributes a large share of votes.”
- “The heatmap suggests at least two preference modes: players who strongly reward Original/MarioDPO-like levels, and players who are more tolerant of exploratory or noisy generators.”
- “Because the sample is anonymous and sparse, we present this as exploratory evidence rather than a definitive taxonomy.”

Avoid:

- Overstated cluster names unless the heatmap clearly supports them.
- Claiming demographic differences; no demographics were collected.
- Treating anonymous browser IDs as guaranteed unique humans.

### Section G — Tags as qualitative failure-mode annotations

Research question:

> RQ5: What extra information do player tags provide beyond the binary vote?

This should be a compact section, not many hypothesis tests.

Analyses:

1. Tag frequency overall.
2. Tag frequency by generator.
3. Tag co-occurrence matrix.
4. Tags over outcome:
   - tags on winning side vs losing side
   - “fun” / “creative” tags among winners
   - “impossible” / “broken_graphics” / “too_hard” among losers
5. Tags versus static metrics:
   - impossible ↔ gap density / early death / low progress
   - broken_graphics ↔ unusual tile entropy / invalid-looking structures if measurable
   - fun/creative ↔ diversity, verticality, path entropy

Figures:

1. Tag distribution bar chart.
2. Tag-by-generator heatmap.
3. Tag co-occurrence network or matrix.
4. A few representative level examples / screenshot references, if available.

Writing angle:

> Tags provide a lightweight semantic layer over votes. They help distinguish why a generator loses: too hard, boring, impossible, broken graphics, etc.

Avoid:

- Long lists of Mann–Whitney tests.
- Treating tags as ground-truth labels. They are sparse, optional, subjective annotations.

### Section H — Platform case study figure

Add a figure from the PCG Arena “Detailed Level Statistics” page.

Purpose:

- Show the reader what the platform enables visually and analytically.
- Demonstrate trajectories, death histogram, tags, level view in one screenshot.

Placeholder in plan:

> TODO Antek: capture a high-resolution screenshot of the Detailed Level Statistics page showing many gameplay traces, death locations, and tag counts.

In the chapter, treat this figure as a platform/research-instrument demonstration, not as a statistical result.

---

## 3. What to remove or demote from the current report

Remove / heavily rewrite:

1. H1 “Optimized Difficulty / Flow Channel”
   - Not appropriate under one-attempt battle design.

2. Repeated “not supported” hypothesis subsections
   - They drain reader attention.

3. Skill-consistency ANOVA section
   - Skill rating is default 1000/RD 350 in current player profile export.
   - If player skill is estimated, use completion/progress only as exploratory behavior, not formal skill.

4. Weak death-rate correlations
   - Death is binary per attempt, not count.

5. Model-performance section with 66% accuracy, unless it is reframed as an appendix
   - With small data and tag leakage, it may feel like overfitting.

6. Judge-function experiments as currently written
   - They may be useful for the MarioDPO chapter, but the EDA chapter should not be a long sequence of ad-hoc experiments.
   - If retained, move to a short “Implications for automatic judge design” subsection after stronger descriptive analyses.

7. Any claim based on null structural columns in `level_stats`
   - Instead compute structural metrics directly from level text files.

Keep / strengthen:

1. Generator ranking.
2. Pairwise confusion matrix.
3. Tag distribution and tag-by-generator heatmap.
4. Trajectory analysis, but make it generator-level and visually strong.
5. User preference clustering/heatmap, expanded.

---

## 4. Proposed figure storyboard

Recommended final figures for the chapter:

1. `fig:study-data-model`
   - Diagram of players → votes → levels → telemetry/tags/trajectories.

2. `fig:eda-engagement`
   - Votes over time + votes per player + cumulative vote contribution.

3. `fig:generator-ranking`
   - Generator ranking by Elo/Bradley–Terry/Glicko with uncertainty.

4. `fig:pairwise-confusion`
   - Pairwise generator confusion matrix, ordered by ranking.
   - Caption says lighter green = higher row-generator win rate.

5. `fig:static-metrics-table`
   - Table, not necessarily figure: linearity, leniency, density, NCD, gap/enemy metrics by generator.

6. `fig:expressive-range`
   - Generator-wise 2D histograms of linearity × leniency or density × leniency.
   - Ordered by ranking.

7. `fig:trajectory-stacks`
   - Generator-wise stacked red trajectories on white background.
   - Ordered by ranking with generator name + rating in each subplot.

8. `fig:trajectory-occupancy`
   - Generator-wise 2D occupancy heatmaps.
   - Ordered by ranking.

9. `fig:behavioral-metrics-vs-rating`
   - Rating vs occupancy entropy / progress / verticality / chokepoint concentration.

10. `fig:user-generator-heatmap`
    - User × generator preference matrix, clustered.

11. `fig:user-embedding`
    - PCA/UMAP of users based on preference/playstyle vectors.

12. `fig:tag-semantics`
    - Tag distribution + tag co-occurrence + tag-by-generator heatmap.

13. `fig:detailed-level-stats-screenshot`
    - Screenshot from platform, showing the research analytics UI.

This is enough. Avoid more than ~12–13 figures unless the chapter becomes too long.

---

## 5. Suggested final research questions

Use five strong research questions instead of ten weak hypotheses.

### RQ1 — Human preference ranking

> Which generators are preferred by players in blind pairwise comparisons?

Expected result:

- Original and MarioDPO top the ranking.
- Pattern-based generators perform poorly.
- Confusion matrix reveals where rankings are stable or contested.

### RQ2 — Static expressive range

> How do the generators differ in structural expressive range, and which static properties align with player preference?

Expected result:

- Generators occupy distinct design-space regions.
- Pattern generators likely separate by gap/density/linearity/repetition.
- Original/MarioDPO may be closer in static style or diversity.

### RQ3 — Gameplay footprint

> What behavioral signatures appear in player trajectories for each generator?

Expected result:

- Stronger generators may show longer progress, broader occupancy, less early termination, and more varied paths.
- Weak generators may show concentrated early deaths or narrow/fragmented traces.

### RQ4 — User heterogeneity

> Are player preferences and play styles homogeneous, or do visible subgroups emerge?

Expected result:

- Use heatmaps and embeddings to show possible preference/playstyle subgroups.
- Present visually and cautiously.

### RQ5 — Tag semantics

> What do optional tags reveal about why players prefer or reject levels?

Expected result:

- Tags identify failure modes and positive qualities.
- Tag-by-generator patterns make generator weaknesses interpretable.

---

## 6. Implementation plan

### Phase 1 — Data consolidation

Tasks:

1. Export all vote pages:
   - Current votes file has 1000 of 1192.
   - Need second page with offset 1000 or update export script to paginate automatically.

2. Export all trajectory pages:
   - Current standalone trajectories file has 100 of 2429.
   - But also parse trajectories embedded in votes.

3. Create a single normalized analysis table:

One row per played side:

- `vote_id`
- `player_id`
- `session_id`
- `created_at_utc`
- `side`
- `generator_id`
- `level_id`
- `opponent_generator_id`
- `result_for_side` = win/loss/tie/skip
- `score_for_side` = 1/0/0.5/missing
- `completed`
- `died` = binary
- `duration_seconds`
- `jumps`
- `coins_collected`
- `enemies_killed`
- `trajectory`
- `death_location`
- `tags`

This table becomes the base for all EDA.

### Phase 2 — Static metric computation

Tasks:

1. Build a level loader:
   - `db/seed/levels/<generator>/*.txt`
   - `MarioDPO/generated_levels_2026_02_01/*.txt`
   - Any other production-only levels if not in repo.

2. Compute metrics:
   - linearly fitted surface / R²
   - leniency
   - tile density
   - gap density
   - enemy density
   - reward density
   - tile entropy
   - unique-column ratio
   - compression ratio
   - within-generator NCD diversity
   - distance to original centroid

3. Join metrics to the normalized side table via `level_id`.

### Phase 3 — Ranking and uncertainty

Tasks:

1. Simple score-rate ranking for readability.
2. Elo or Bradley–Terry ranking for pairwise robustness.
3. Bootstrap confidence intervals:
   - bootstrap votes
   - optionally bootstrap players for player-level uncertainty

### Phase 4 — Plot generation

Recommended new scripts:

- `eda/07_replanned_analysis/load_data.py`
- `eda/07_replanned_analysis/compute_static_metrics.py`
- `eda/07_replanned_analysis/compute_rankings.py`
- `eda/07_replanned_analysis/plot_expressive_range.py`
- `eda/07_replanned_analysis/plot_generator_trajectories.py`
- `eda/07_replanned_analysis/plot_user_preferences.py`
- `eda/07_replanned_analysis/plot_tags.py`

Recommended plot output directory:

- `latex/main_report/img/eda_2026_05/`

Then either update `\graphicspath` or use relative paths in `\includegraphics`.

### Phase 5 — Rewrite chapter

Rewrite the chapter around the five RQs above.

Tone:

- Descriptive and visual first.
- Use statistical tests only where they support a clear point.
- Avoid “not supported” treadmill.
- Be explicit about platform limitations.
- Emphasize that this is a real deployed system collecting real preference data.

---

## 7. Proposed writing skeleton

```text
Section: User Study and Exploratory Analysis

1. Study protocol and dataset
   - recruitment corrected
   - anonymous cookie/player IDs
   - one-shot blind A/B design
   - data table
   - limitations

2. Generator preference ranking
   - ranking figure
   - confusion matrix
   - core observation: Original and MarioDPO strongest; pattern generators weakest

3. Static expressive range of generators
   - metrics definitions
   - metrics table
   - expressive range plot
   - relation to ranking

4. Gameplay trajectories as behavioral fingerprints
   - stacked red trajectory figure
   - occupancy histogram figure
   - derived path diversity/coverage metrics
   - example detailed-level-stats screenshot

5. User preference heterogeneity
   - engagement concentration
   - user × generator heatmap
   - user embedding / possible clusters
   - cautious interpretation

6. Tag semantics and failure modes
   - tag distribution
   - tag-by-generator heatmap
   - tag co-occurrence
   - what tags add beyond votes

7. Summary
   - PCG Arena can rank generators
   - structural metrics explain part of the story
   - trajectories expose navigability and failure modes
   - users are not necessarily homogeneous
   - tags provide lightweight qualitative diagnostics
```

---

## 8. Notes for `data.md`

`eda/data.md` is useful as a schema inventory, but it should be updated after final data consolidation.

Needed corrections/additions:

1. Clarify that `player_id` is anonymous browser/player identifier, not guaranteed unique person.
2. Clarify that session continuity is via browser identifiers/session IDs, not linked accounts.
3. Clarify death count is binary under current one-attempt design.
4. Clarify that standalone trajectories export is paginated, while vote telemetry contains many embedded trajectories.
5. Mention that the current votes export is incomplete due to limit=1000.
6. Add a section: “Analysis-ready derived tables” after scripts are implemented.

---

## 9. Final high-level strategy

The rewritten EDA should stop trying to prove universal statements like “moderate difficulty is best.” Instead, it should show what PCG Arena uniquely provides:

- A live human-preference ranking of generators.
- Pairwise comparison structure with interpretable head-to-head outcomes.
- Structural expressive-range comparison using standard PCG metrics.
- Real gameplay trajectories showing how players interact with generated levels.
- User-level preference maps suggesting heterogeneity.
- Tags that explain why levels win or lose.

That is a much stronger contribution and a more interesting story for both PCG researchers and readers of the report.
