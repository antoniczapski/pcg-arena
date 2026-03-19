"""
Enriched citations.json with reference_document and reference_citation fields.

This file maps each citation key to:
  - reference_document: path(s) to ACTUAL PAPER EXTRACTIONS in latex/literature_review/
  - reference_citation: what the reference document actually says about the claim

IMPORTANT: Only human-authored paper extractions are used as reference_documents.
AI-generated summaries (*_background.md, deep_research_reports/*.md) are EXCLUDED.
"""

import json
from pathlib import Path

# Load the extracted citations
citations_path = Path(__file__).parent / "citations.json"
data = json.loads(citations_path.read_text(encoding="utf-8"))

LIT = "latex/literature_review"

enrichments = {
    "bradley1952rank": {
        "reference_documents": [
            f"{LIT}/additional/bradley1952-rank-analysis-paired-comparisons.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "All modern skill-rating systems rest on the Bradley-Terry model: P(i > j) = pi_i / (pi_i + pi_j)",
                "reference_citation": "Bradley & Terry (1952) proposed the paired-comparison model. The paper defines the probability that item i is preferred to j as pi_i/(pi_i+pi_j). See the original paper: 'Rank Analysis of Incomplete Block Designs: I. The Method of Paired Comparisons', Biometrika 39(3/4), 324-345.",
            }
        },
    },
    "chiang2024chatbot": {
        "reference_documents": [
            f"{LIT}/rankings_and_rlhf/chiang2024-chatbot-arena.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Chiang et al. deployed a web platform where users chat simultaneously with two anonymous LLMs and vote for the better response. Over 240,000 votes from 90,000+ users have been collected; rankings are computed via Bradley-Terry MLE. Active sampling strategy concentrates votes on close model pairs.",
                "reference_citation": "chiang2024-chatbot-arena.md confirms: '240K+ votes', Bradley-Terry model and Elo ratings for ranking, 'active sampling strategy concentrates votes on model pairs with close ratings, maximising information gain per comparison.'",
            }
        },
    },
    "christiano2017deep": {
        "reference_documents": [
            f"{LIT}/rankings_and_rlhf/christiano2017-deep-rl-human-preferences.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Christiano et al. proposed learning a reward model from pairwise trajectory comparisons and optimising the policy against it via PPO. Applied to Atari and MuJoCo.",
                "reference_citation": "christiano2017-deep-rl-human-preferences.md confirms: 'Learns a reward function from non-expert human preferences between trajectory segment pairs, then optimises RL policy against the learned reward.' Applied to Atari and MuJoCo. 'Solves complex RL tasks with feedback on <1% of agent-environment interactions.'",
            }
        },
    },
    "dahlskog2014procedural": {
        "reference_documents": [
            f"{LIT}/seed_generators/horn2014-comparative-evaluation-mario-generators.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Three Pattern-based generators represent levels as sequences of micro-patterns extracted from original SMB levels and use evolutionary search with different fitness functions: pattern count, pattern occurrence, and weighted pattern count.",
                "reference_citation": "horn2014-comparative-evaluation-mario-generators.md describes the Dahlskog & Togelius pattern-based generators in detail: '23 micro-patterns extracted from original SMB levels; 43 meso-pattern rules across 5 pattern categories.' NOTE: The Dahlskog & Togelius 2014 paper itself does not have its own .md extraction — it is cross-referenced via horn2014.",
            }
        },
    },
    "elo1978rating": {
        "reference_documents": [
            f"{LIT}/additional/elo1978-rating-of-chessplayers.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Elo operationalised the Bradley-Terry model for competitive chess. Expected score E_A = 1/(1+10^((R_B-R_A)/400)). Update: R_A' = R_A + K(S_A - E_A).",
                "reference_citation": "elo1978-rating-of-chessplayers.md: Elo system described with 'expected score', 'performance rating formula', rating difference scaled by 400, and K-factor update rule.",
            }
        },
    },
    "glickman1999parameter": {
        "reference_documents": [
            f"{LIT}/rankings_and_rlhf/glickman1999-parameter-estimation-paired-comparison.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Glickman recast Elo in a Bayesian framework (Glicko), modelling each player's rating as a Gaussian N(mu, sigma^2) where sigma (rating deviation) quantifies uncertainty. Between rating periods, RD grows to reflect increased uncertainty from inactivity.",
                "reference_citation": "glickman1999-parameter-estimation-paired-comparison.md confirms: 'A non-iterative algorithm for dynamic paired comparison models extending Bradley-Terry with uncertainty tracking.' 'Reparameterised win probability: P(win) = 1/(1+10^((theta_i-theta_j)/400)); prior distribution N(1500, sigma_0^2).' 'Incorporates rating deviation (RD) — uncertainty increases over time via sigma_t^2 growth model.' Applied to 30,000+ USCF chess players.",
            }
        },
    },
    "glickman2012glicko2": {
        "reference_documents": [
            f"{LIT}/additional/glickman2012-example-glicko2-system.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Glicko-2 extends Glicko with a third parameter, volatility sigma_v, which captures how erratic an entity's performance is. The update pipeline converts ratings to an internal scale, estimates variance and improvement from outcomes, iteratively updates volatility, and then updates RD and rating.",
                "reference_citation": "glickman2012-example-glicko2-system.md is the Glicko-2 technical report describing the full algorithm: volatility parameter, the update pipeline (convert to internal scale, compute variance, iteratively solve for volatility, update RD and rating).",
            },
            1: {
                "thesis_claim": "PCG Arena uses the Glicko-2 rating system to maintain uncertainty-aware rankings.",
                "reference_citation": "This is a factual system design claim about PCG Arena itself, supported by glickman2012-example-glicko2-system.md which defines the algorithm.",
            },
        },
    },
    "horn2014comparative": {
        "reference_documents": [
            f"{LIT}/pcg/horn2014-comparative-evaluation-level-generators.md",
            f"{LIT}/seed_generators/horn2014-comparative-evaluation-mario-generators.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Automated structural metrics such as linearity, leniency, and density are widely used for characterising generator output.",
                "reference_citation": "horn2014-comparative-evaluation-level-generators.md defines and uses 6 expressivity metrics (linearity, leniency, density, pattern density, pattern variation, compression distance) to compare 7 generators plus original SMB levels.",
            },
            1: {
                "thesis_claim": "Later works (horn2014, summerville2017) use R^2 goodness-of-fit for linearity instead of Smith's original definition, inverting the scale.",
                "reference_citation": "horn2014-comparative-evaluation-level-generators.md uses a linearity metric defined differently from Smith & Whitehead (2010). Uses R^2 goodness-of-fit.",
            },
            2: {
                "thesis_claim": "Compression distance (NCD) is used as a diversity proxy.",
                "reference_citation": "horn2014-comparative-evaluation-level-generators.md uses NCD (gzip-based Normalized Compression Distance) as one of 6 evaluation metrics. States that original SMB levels have highest compression distance.",
            },
            3: {
                "thesis_claim": "ERA has been widely adopted (horn2014, shaker2012).",
                "reference_citation": "horn2014-comparative-evaluation-level-generators.md performs ERA across all 7 generators, generating 1000 levels per generator and plotting joint distributions of linearity vs. leniency.",
            },
        },
    },
    "karakovskiy2012marioai": {
        "reference_documents": [
            f"{LIT}/additional/karakovskiy2012-mario-ai-benchmark-competitions.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "The open-source Mario AI Framework offers a standardised environment for both automated and human evaluation.",
                "reference_citation": "karakovskiy2012-mario-ai-benchmark-competitions.md describes the Mario AI Framework: an open-source Java implementation of Infinite Mario Bros providing the standard experimental environment, competition tracks, and standardised level format.",
            },
            1: {
                "thesis_claim": "The Notch generator shipped with Infinite Mario Bros is the canonical constructive example.",
                "reference_citation": "karakovskiy2012-mario-ai-benchmark-competitions.md describes the original Infinite Mario Bros game by Markus Persson (Notch) and its built-in level generator.",
            },
            2: {
                "thesis_claim": "The Mario AI Framework is an open-source Java implementation based on Infinite Mario Bros, created by Markus Persson in 2008. Served as basis for three championship tracks.",
                "reference_citation": "karakovskiy2012-mario-ai-benchmark-competitions.md confirms: the framework served as basis for three tracks (Gameplay, Learning, Level Generation) of the Mario AI Championship (2009-2012). Created by Markus Persson (Notch).",
            },
            3: {
                "thesis_claim": "The game engine was ported from the Java-based Mario AI Framework to TypeScript.",
                "reference_citation": "This is a factual claim about the PCG Arena system design. karakovskiy2012-mario-ai-benchmark-competitions.md is the source for the Mario AI Framework being ported.",
            },
        },
    },
    "khalifa2020pcgrl": {
        "reference_documents": [
            f"{LIT}/additional/khalifa2020-pcgrl-procedural-content-generation-rl.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "PCGRL formulates level design as an MDP and trains an RL agent to edit tile grids, bypassing the need for training data entirely.",
                "reference_citation": "khalifa2020-pcgrl-procedural-content-generation-rl.md describes PCGRL: framing level design as an MDP where an agent iteratively edits a tile grid, receiving reward for satisfying playability and design constraints. Unlike PCGML, PCGRL requires no training corpus.",
            },
            1: {
                "thesis_claim": "A* agent playability check is the most common first stage in PCG evaluation pipelines (volz2018, summerville2016, khalifa2020).",
                "reference_citation": "khalifa2020-pcgrl-procedural-content-generation-rl.md uses agent-based playability checks as part of its evaluation pipeline.",
            },
        },
    },
    "marino2015empirical": {
        "reference_documents": [
            f"{LIT}/pcg/marino2015-empirical-evaluation-metrics.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Marino et al. demonstrated that automated metrics only weakly correlate with human-rated difficulty and enjoyment, concluding that 'current computational metrics should not be used in lieu of user studies.'",
                "reference_citation": "marino2015-empirical-evaluation-metrics.md confirms: 'Two PCG systems rated identically by all computational metrics were rated significantly differently by humans on enjoyment.' 'Leniency only weakly correlated with human-rated difficulty.' n=37 participants, 7-point Likert scales.",
            },
            1: {
                "thesis_claim": "Controlled lab studies use 15-37 participants (shaker2011, marino2015).",
                "reference_citation": "marino2015-empirical-evaluation-metrics.md: n=37 participants.",
            },
            2: {
                "thesis_claim": "At least three incompatible leniency formulations exist (smith2010, shaker2012, marino2015).",
                "reference_citation": "marino2015-empirical-evaluation-metrics.md discusses leniency and its definition, contributing one of at least three incompatible formulations across the literature.",
            },
            3: {
                "thesis_claim": "Leniency only weakly correlates with human-rated difficulty.",
                "reference_citation": "marino2015-empirical-evaluation-metrics.md: direct finding — 'Leniency only weakly correlated with human-rated difficulty.'",
            },
            4: {
                "thesis_claim": "Marino et al. used 7-point Likert scales for enjoyment, aesthetics, and difficulty (n=37).",
                "reference_citation": "marino2015-empirical-evaluation-metrics.md confirms: 'User study with n=37 participants using 7-point Likert scales.'",
            },
            5: {
                "thesis_claim": "Two generators rated identically by all computational metrics were rated significantly differently by human players on enjoyment.",
                "reference_citation": "marino2015-empirical-evaluation-metrics.md: 'Two PCG systems rated identically by all computational metrics were rated significantly differently by humans on enjoyment.' This is the paper's key finding.",
            },
            6: {
                "thesis_claim": "Automated PCG metrics fail to capture fun, aesthetics, or challenge appropriateness (in context of metric mismatch parallel with ROUGE).",
                "reference_citation": "marino2015-empirical-evaluation-metrics.md concludes that computational metrics are insufficient proxies for player experience.",
            },
        },
    },
    "mawhorter2010occupancy": {
        "reference_documents": [
            f"{LIT}/seed_generators/mawhorter2010-ore-occupancy-regulated-extension.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "ORE builds levels by iteratively attaching hand-authored chunks at compatible anchor points, producing structurally distinctive levels.",
                "reference_citation": "mawhorter2010-ore-occupancy-regulated-extension.md confirms: 'Assembles levels from a library of 42 hand-authored chunks (up to 10x10 tiles) using anchor points.' 'Three iterative steps: context selection, chunk selection, chunk integration.' 'Prioritises variety over playability.'",
            }
        },
    },
    "nam2024using": {
        "reference_documents": [
            f"{LIT}/pcg/nam2024-rl-quality-diversity.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Virtual damage from stochastic 'human-like' agents that model input timing inaccuracies.",
                "reference_citation": "nam2024-rl-quality-diversity.md confirms: 'Introduces human-like AI agents with input timing inaccuracies for more realistic difficulty assessment.' 'Difficulty = total damage (enemy hits + hole falls) with hole coefficient 1.1.' Human study (n=33) validates the approach.",
            }
        },
    },
    "ouyang2022training": {
        "reference_documents": [
            f"{LIT}/rankings_and_rlhf/ouyang2022-instructgpt-training-language-models-instructions.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Ouyang et al. codified the three-step recipe (SFT -> Reward Model -> PPO). A 1.3B InstructGPT was preferred over 175B GPT-3, demonstrating that alignment quality matters more than model scale.",
                "reference_citation": "ouyang2022-instructgpt-training-language-models-instructions.md confirms: '1.3B InstructGPT preferred over 175B GPT-3 (100x fewer parameters); 175B InstructGPT preferred 85 plus/minus 3% over 175B GPT-3.' Three-step recipe: SFT, RM, PPO.",
            }
        },
    },
    "pedersen2010modeling": {
        "reference_documents": [
            f"{LIT}/pcg/pedersen2010-modeling-player-experience.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Larger web-based studies sacrifice experimental control (pedersen2010).",
                "reference_citation": "pedersen2010-modeling-player-experience.md confirms a web-based study design with 181 subjects.",
            },
            1: {
                "thesis_claim": "Pedersen et al. recruited 181 subjects to play Infinite Mario Bros variants and report pairwise affective preferences.",
                "reference_citation": "pedersen2010-modeling-player-experience.md confirms: '120-181 subjects (240 game pairs, 480 sessions).' 'Uses neuroevolutionary preference learning to model player experience.' '4 controllable level parameters; 6 affective states modeled.'",
            },
        },
    },
    "rafailov2023direct": {
        "reference_documents": [
            f"{LIT}/rankings_and_rlhf/rafailov2023-direct-preference-optimization.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Rafailov et al. observed that the optimal RLHF policy can be expressed in closed form as a function of the reward model. Substituting back yields DPO, which directly fine-tunes the policy using preference pairs — eliminating the reward model and RL loop. DPO matched or exceeded PPO-based RLHF on sentiment, summarisation, and dialogue.",
                "reference_citation": "rafailov2023-direct-preference-optimization.md confirms: 'Key insight: analytical change-of-variables from Bradley-Terry reward model to optimal policy yields a simple binary cross-entropy loss.' 'Matches or exceeds PPO-based RLHF on sentiment, summarisation, and dialogue tasks.' 'Policy network implicitly represents both language model and reward.'",
            }
        },
    },
    "sarkar2017glicko2": {
        "reference_documents": [
            f"{LIT}/rankings_and_rlhf/sarkar2017-player-rating-matchmaking-human-computation.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Sarkar applied Glicko-2 to the human computation game Paradox, treating both players and puzzle-tasks as rated entities. This is the most direct precedent for PCG Arena's design.",
                "reference_citation": "sarkar2017-player-rating-matchmaking-human-computation.md confirms: 'Uses Glicko-2 rating system for difficulty balancing in Paradox.' 'Both matchmaking-based and difficulty-based ordering led to significantly more attempted/completed levels than random ordering.' n=294.",
            }
        },
    },
    "schrum2025mariodiffusion": {
        "reference_documents": [
            f"{LIT}/seed_generators/schrum2025-mariodiffusion-text-to-level.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "MarioDiffusion uses a text-conditioned UNet denoiser to generate 16x16-tile scenes from natural-language captions, representing the latest generation of multimodal PCG.",
                "reference_citation": "schrum2025-mariodiffusion-text-to-level.md confirms: 'Text-conditioned diffusion model for Super Mario Bros level generation.' '16x16 scenes extracted via sliding window.' 'Deterministic caption assignment from scene features.'",
            },
            1: {
                "thesis_claim": "MarioDiffusion generates tile scenes from natural-language captions via a diffusion model.",
                "reference_citation": "Same source confirms this.",
            },
        },
    },
    "shaker2011features": {
        "reference_documents": [
            f"{LIT}/pcg/shaker2011-feature-analysis-game-content-quality.md",
            f"{LIT}/additional/shaker2011-feature-analysis-game-content-quality.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "A follow-up by Shaker et al. collected 600 game-pair comparisons via an uncontrolled web applet, predating modern ML-based generators.",
                "reference_citation": "shaker2011-feature-analysis-game-content-quality.md: 'data set of 600 human players', 'based on the 600 game pairs that have been collected', data collected via Internet Java applet advertised on 'social networks, mailing lists and blogs'.",
            }
        },
    },
    "shaker2011mario": {
        "reference_documents": [
            f"{LIT}/additional/shaker2011-mario-level-generation-track.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Controlled lab studies use 15-37 participants (shaker2011mario).",
                "reference_citation": "shaker2011-mario-level-generation-track.md describes the Level Generation Track competition. The evaluation used 15 human judges in pairwise forced-choice.",
            },
            1: {
                "thesis_claim": "The Mario AI Level Generation Competition featured several search-based entries.",
                "reference_citation": "shaker2011-mario-level-generation-track.md describes all competing generators in the Level Generation Track.",
            },
            2: {
                "thesis_claim": "The Level Generation Track was the first academic PCG competition. Generators received gameplay metrics from a test level and had 60 seconds to produce a personalised level. Six entries competed; evaluation used pairwise forced-choice with 15 human judges.",
                "reference_citation": "shaker2011-mario-level-generation-track.md describes all details: first academic PCG competition, 60-second time limit, 6 entries, pairwise human evaluation.",
            },
            3: {
                "thesis_claim": "NotchParam exposing six tunable difficulty/style knobs.",
                "reference_citation": "shaker2011-mario-level-generation-track.md describes the NotchParam generator and its parameterization.",
            },
            4: {
                "thesis_claim": "The Mario AI Championship asked 15 judges to play two levels and select 'which was more fun?' This protocol directly inspired PCG Arena's design.",
                "reference_citation": "shaker2011-mario-level-generation-track.md describes the pairwise 'which was more fun?' evaluation protocol. The 'directly inspired PCG Arena's design' is a thesis-level interpretive claim.",
            },
        },
    },
    "shaker2012evolving": {
        "reference_documents": [
            f"{LIT}/pcg/shaker2012-evolving-levels-grammatical-evolution.md",
            f"{LIT}/seed_generators/shaker2012-grammatical-evolution-mario-levels.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Shaker et al. used Grammatical Evolution (GE) to map integer genotypes to level phenotypes via context-free grammar productions, combining interpretability of grammars with evolutionary search.",
                "reference_citation": "shaker2012-evolving-levels-grammatical-evolution.md confirms: 'Uses Grammatical Evolution to evolve playable 2D platformer levels using context-free design grammars.' '8 chunk types; context-free grammar maps integer genotypes to phenotypes.'",
            },
            1: {
                "thesis_claim": "The GE generator evolves level-construction programs via a context-free grammar.",
                "reference_citation": "Same source. shaker2012-grammatical-evolution-mario-levels.md confirms the GE mechanism.",
            },
            2: {
                "thesis_claim": "At least three incompatible leniency formulations exist (smith2010, shaker2012, marino2015).",
                "reference_citation": "shaker2012-evolving-levels-grammatical-evolution.md uses its own leniency definition, contributing one of the three incompatible formulations.",
            },
            3: {
                "thesis_claim": "NCD is used as a diversity proxy (shaker2012, horn2014).",
                "reference_citation": "shaker2012-evolving-levels-grammatical-evolution.md uses NCD. States: 'NCD > 0.6 indicates substantial dissimilarity; gzip-based compression distance used for structural diversity measurement.'",
            },
            4: {
                "thesis_claim": "ERA has been widely adopted (horn2014, shaker2012).",
                "reference_citation": "shaker2012-evolving-levels-grammatical-evolution.md performs ERA with linearity, leniency, density metrics.",
            },
        },
    },
    "smith2010analyzing": {
        "reference_documents": [
            f"{LIT}/pcg/smith2010-analyzing-expressive-range.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Automated structural metrics such as linearity, leniency, and density are widely used for characterising generator output (smith2010, horn2014).",
                "reference_citation": "smith2010-analyzing-expressive-range.md defines the founding metrics: 'Two founding metrics: linearity and leniency.' This paper introduced ERA as the dominant characterisation method.",
            },
            1: {
                "thesis_claim": "Smith & Whitehead introduced Launchpad, a rhythm-based generator mapping player actions to level geometry via a design grammar. The same paper introduced Expressive Range Analysis (ERA).",
                "reference_citation": "smith2010-analyzing-expressive-range.md confirms: 'Introduces the concept of Expressive Range Analysis (ERA) for evaluating PCG generators. Applied to Launchpad, a rhythm-based 2D platformer level generator.' 'Framework: determine metrics, generate content (1000-10000 levels), visualise generative space as 2D histograms.'",
            },
            2: {
                "thesis_claim": "Smith et al. defined linearity via linear regression on platform midpoints.",
                "reference_citation": "smith2010-analyzing-expressive-range.md defines linearity as height variation/profile metric using regression.",
            },
            3: {
                "thesis_claim": "At least three incompatible leniency formulations exist (smith2010, shaker2012, marino2015).",
                "reference_citation": "smith2010-analyzing-expressive-range.md defines leniency as 'difficulty approximation via weighted component scores.'",
            },
            4: {
                "thesis_claim": "ERA, introduced by Smith & Whitehead, generates a large sample of levels, computes two metrics per level, and visualises the joint distribution as a 2D histogram.",
                "reference_citation": "smith2010-analyzing-expressive-range.md: 'Framework: determine metrics, generate content (1000-10000 levels), visualise generative space as 2D histograms, analyse parameter impact.' 'ERA is descriptive, not evaluative.'",
            },
        },
    },
    "snow2008cheap": {
        "reference_documents": [
            f"{LIT}/rankings_and_rlhf/snow2008-cheap-fast-non-expert-annotations.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Snow et al. showed that aggregating labels from multiple non-expert annotators can match expert-level quality.",
                "reference_citation": "snow2008-cheap-fast-non-expert-annotations.md confirms: '5 tasks: affect recognition, word similarity, recognising textual entailment, event temporal ordering, word sense disambiguation.' 'High agreement between non-expert and gold-standard labels for all 5 tasks.' '10 independent annotations collected per item.'",
            }
        },
    },
    "stiennon2020learning": {
        "reference_documents": [
            f"{LIT}/rankings_and_rlhf/stiennon2020-learning-summarize-human-feedback.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Stiennon et al. scaled RLHF to summarisation (6.7B model, 64K comparisons) and showed that the learned reward predicts human preferences better than ROUGE.",
                "reference_citation": "stiennon2020-learning-summarize-human-feedback.md confirms: 'Reddit TL;DR dataset: 123,169 posts; 64,832 summary comparisons collected.' 'Models up to 6.7B parameters.' 'Reward model outperforms ROUGE at predicting human preferences.'",
            },
            1: {
                "thesis_claim": "Just as ROUGE fails to capture summary quality (stiennon2020), automated PCG metrics fail to capture fun.",
                "reference_citation": "stiennon2020-learning-summarize-human-feedback.md: 'Reward model outperforms ROUGE at predicting human preferences.' This supports the metric mismatch analogy.",
            },
        },
    },
    "sudhakaran2023mariogpt": {
        "reference_documents": [
            f"{LIT}/seed_generators/sudhakaran2023-mariogpt-text2level-generation.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "MarioGPT fine-tunes DistilGPT-2 on column-tokenised Mario levels with text-prompt conditioning, enabling the first natural-language-controllable level generator. 88% of generated levels are playable without post-processing.",
                "reference_citation": "sudhakaran2023-mariogpt-text2level-generation.md confirms: 'Fine-tunes DistilGPT-2 on VGLC corpus; uses frozen BART encoder for cross-attention conditioning on text prompts.' '88% of generated levels are playable without post-processing.' 'First text-to-level model.'",
            },
            1: {
                "thesis_claim": "MarioGPT uses a fine-tuned DistilGPT-2 with text-prompt control.",
                "reference_citation": "Same source confirms this.",
            },
        },
    },
    "summerville2016super": {
        "reference_documents": [
            f"{LIT}/pcg/summerville2016-learning-player-tailored-content.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Summerville & Mateas trained a 3-layer LSTM to generate levels column-by-column using a 'snaking' tokenisation that preserves vertical adjacency. Co-generating levels with A*-agent play traces achieved 97% playability.",
                "reference_citation": "summerville2016-learning-player-tailored-content.md confirms: '3-layer LSTM architecture with 512 units; column-major snaking tokenisation preserves vertical adjacency.' 'LSTM-generated levels completed by AI at 97% rate.' 'Play traces extracted from YouTube video using OpenCV.'",
            },
            1: {
                "thesis_claim": "The Video Game Level Corpus (VGLC) standardised the ASCII tilemap encoding across all 32 original SMB levels.",
                "reference_citation": "summerville2016-learning-player-tailored-content.md introduces/uses the VGLC and the standardised tilemap encoding.",
            },
            2: {
                "thesis_claim": "A* agent playability check is the most common first stage in PCG evaluation pipelines (volz2018, summerville2016, khalifa2020).",
                "reference_citation": "summerville2016-learning-player-tailored-content.md uses A* agent for playability evaluation (97% completion rate reported).",
            },
        },
    },
    "summerville2017understanding": {
        "reference_documents": [
            f"{LIT}/additional/summerville2017-understanding-mario-evaluation-metrics.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Later works (horn2014, summerville2017) use R^2 goodness-of-fit for linearity, inverting the scale.",
                "reference_citation": "summerville2017-understanding-mario-evaluation-metrics.md discusses linearity metrics and their definitions across the literature.",
            },
            1: {
                "thesis_claim": "Summerville et al. collected ratings across 85 design metrics and showed that inter-rater agreement imposes ceilings on achievable metric-human correlations.",
                "reference_citation": "summerville2017-understanding-mario-evaluation-metrics.md evaluates design metrics against human ratings and measures inter-rater agreement bounds, showing aesthetics are inherently noisy — capping achievable metric-human correlations.",
            },
            2: {
                "thesis_claim": "Summerville et al. further demonstrated that inter-rater agreement imposes ceilings on metric-human correlations, with aesthetics being particularly noisy.",
                "reference_citation": "Same source as occurrence 1.",
            },
        },
    },
    "summerville2018pcgml": {
        "reference_documents": [
            f"{LIT}/additional/summerville2018-pcgml-procedural-content-generation-ml.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "PCG refers to the algorithmic creation of game content with limited or indirect human input (togelius2011, summerville2018).",
                "reference_citation": "summerville2018-pcgml-procedural-content-generation-ml.md is the PCGML survey defining PCG via machine learning. It provides the standard definition and taxonomy.",
            },
            1: {
                "thesis_claim": "The most common taxonomy (togelius2011, summerville2018) distinguishes five generation paradigms.",
                "reference_citation": "summerville2018-pcgml-procedural-content-generation-ml.md presents the taxonomy of PCG approaches.",
            },
            2: {
                "thesis_claim": "PCGML trains neural networks on existing content to learn implicit design knowledge.",
                "reference_citation": "summerville2018-pcgml-procedural-content-generation-ml.md is the defining paper for the PCGML paradigm. Describes training neural networks on existing human-designed content.",
            },
        },
    },
    "togelius2011search": {
        "reference_documents": [
            f"{LIT}/additional/togelius2011-search-based-pcg-taxonomy-survey.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "PCG refers to the algorithmic creation of game content with limited or indirect human input.",
                "reference_citation": "togelius2011-search-based-pcg-taxonomy-survey.md is the primary PCG survey defining the term and proposing the search-based PCG taxonomy.",
            },
            1: {
                "thesis_claim": "PCG is the algorithmic creation of game content with limited or indirect human input.",
                "reference_citation": "Same as occurrence 0.",
            },
            2: {
                "thesis_claim": "The most common taxonomy (togelius2011, summerville2018) distinguishes five generation paradigms.",
                "reference_citation": "togelius2011-search-based-pcg-taxonomy-survey.md proposes the taxonomy of PCG approaches.",
            },
            3: {
                "thesis_claim": "Search-Based PCG (SBPCG) frames content generation as an optimisation problem.",
                "reference_citation": "togelius2011-search-based-pcg-taxonomy-survey.md: 'Search-based PCG frames generation as optimisation.' This is the core concept of the paper.",
            },
        },
    },
    "volz2018evolving": {
        "reference_documents": [
            f"{LIT}/pcg/volz2018-evolving-mario-latent-space-gan.md",
            f"{LIT}/seed_generators/volz2018-mariogan-latent-space-evolution.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Agent-derived features such as jump count or completion fraction provide scalable difficulty estimates.",
                "reference_citation": "volz2018-evolving-mario-latent-space-gan.md confirms: 'Fitness functions optimize tile distribution, playability (A* agent), and jumping actions (jump cost set to 2, other actions cost 1).' Uses agent-derived metrics as difficulty proxies.",
            },
            1: {
                "thesis_claim": "MarioGAN combines a learned GAN with CMA-ES search in its latent space (hybrid paradigm).",
                "reference_citation": "volz2018-evolving-mario-latent-space-gan.md confirms: 'DCGAN trained on segments from one level; CMA-ES searches latent space to optimise fitness functions.' Established the Latent Variable Evolution (LVE) paradigm.",
            },
            2: {
                "thesis_claim": "More recent work has applied CMA-ES to the latent space of trained generative models, combining search-based and ML-based paradigms.",
                "reference_citation": "Same source. volz2018-mariogan-latent-space-evolution.md confirms: 'Established the Latent Variable Evolution (LVE) paradigm for PCGML.'",
            },
            3: {
                "thesis_claim": "MarioGAN trains a DCGAN on sliding-window segments from a single original SMB level. CMA-ES then searches the GAN's latent space to optimise fitness functions.",
                "reference_citation": "volz2018-evolving-mario-latent-space-gan.md: 'GAN maps 32-dimensional latent vectors to 28x14 tile grids; trained on sliding-window segments from one original level.' volz2018-mariogan-latent-space-evolution.md confirms all details.",
            },
            4: {
                "thesis_claim": "MarioGAN combines a DCGAN with CMA-ES latent-space search.",
                "reference_citation": "Same source, confirmed.",
            },
            5: {
                "thesis_claim": "A* agent playability check is the most common first stage in PCG evaluation pipelines (volz2018, summerville2016, khalifa2020).",
                "reference_citation": "volz2018-evolving-mario-latent-space-gan.md uses A* agent for playability evaluation in its fitness function.",
            },
        },
    },
    "yannakakis2011experience": {
        "reference_documents": [
            f"{LIT}/additional/yannakakis2011-experience-driven-pcg.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Online generation enables personalisation but imposes stricter time budgets — a theme central to experience-driven PCG.",
                "reference_citation": "yannakakis2011-experience-driven-pcg.md describes experience-driven PCG: generators optimising empirically derived player models for adaptive/personalized content generation.",
            }
        },
    },
    "zheng2023judging": {
        "reference_documents": [
            f"{LIT}/rankings_and_rlhf/zheng2023-judging-llm-as-judge.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Zheng et al. studied using GPT-4 as a surrogate judge for pairwise evaluation, achieving >80% agreement with human preferences.",
                "reference_citation": "zheng2023-judging-llm-as-judge.md confirms: 'GPT-4 achieves >80% agreement with human preferences.' 'Identifies biases: position bias, verbosity bias, self-enhancement bias.' '3,000 expert votes + 30,000 crowdsourced conversations.'",
            }
        },
    },
    "ziegler2019fine": {
        "reference_documents": [
            f"{LIT}/rankings_and_rlhf/ziegler2019-finetuning-language-models-human-preferences.md",
        ],
        "reference_citations": {
            0: {
                "thesis_claim": "Ziegler et al. adapted the RLHF scheme to language models (GPT-2) and introduced a KL penalty beta*KL[pi || pi_ref] to prevent drift from the pretrained model.",
                "reference_citation": "ziegler2019-finetuning-language-models-human-preferences.md confirms: 'Adapts RLHF to language models (774M GPT-2). Four tasks: positive sentiment, physically descriptive, TL;DR summarisation, CNN/DM summarisation.' 'Introduces KL penalty beta*KL(pi || rho) to prevent policy drift.' '5,000 human comparisons; fine-tuned model preferred 86% vs zero-shot.'",
            }
        },
    },
}

# Apply enrichments to the citations data
for citation in data["citations"]:
    key = citation["citation_key"]
    if key in enrichments:
        enr = enrichments[key]
        citation["reference_documents"] = enr["reference_documents"]

        for i, occ in enumerate(citation["occurrences"]):
            if i in enr["reference_citations"]:
                ref_info = enr["reference_citations"][i]
                occ["thesis_claim"] = ref_info["thesis_claim"]
                occ["reference_citation"] = ref_info["reference_citation"]
            else:
                last_key = max(k for k in enr["reference_citations"].keys() if k <= i)
                ref_info = enr["reference_citations"][last_key]
                occ["thesis_claim"] = ref_info["thesis_claim"]
                occ["reference_citation"] = ref_info["reference_citation"]
    else:
        citation["reference_documents"] = ["NOT FOUND"]
        for occ in citation["occurrences"]:
            occ["thesis_claim"] = "UNKNOWN"
            occ["reference_citation"] = "NO REFERENCE DOCUMENT FOUND"

# Identify papers with no reference documents
no_ref_docs = []
incomplete_refs = []
for citation in data["citations"]:
    key = citation["citation_key"]
    if key in enrichments:
        docs = enrichments[key]["reference_documents"]
        if len(docs) == 0:
            no_ref_docs.append(key)
        for ref_cit in enrichments[key]["reference_citations"].values():
            if "WARNING" in ref_cit.get("reference_citation", "") or "NO DEDICATED" in ref_cit.get("reference_citation", ""):
                if key not in incomplete_refs:
                    incomplete_refs.append(key)

data["papers_with_no_reference_document"] = sorted(no_ref_docs)
data["papers_with_incomplete_extraction"] = sorted(incomplete_refs)
data["notes"] = (
    "ONLY actual paper extractions are used as reference_documents. "
    "AI-generated summaries (*_background.md, deep_research_reports/*.md) are EXCLUDED. "
    "Papers in 'papers_with_no_reference_document' have no PDF/.md available. "
    "Papers in 'papers_with_incomplete_extraction' have .md files that are empty/incomplete or no dedicated extraction."
)

# Write enriched output
out_path = Path(__file__).parent / "citations.json"
out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Enriched citations written to {out_path}")
print(f"\nPapers with NO reference document: {sorted(no_ref_docs)}")
print(f"Papers with incomplete/missing .md extraction: {sorted(incomplete_refs)}")
print(f"Total citation keys: {len(enrichments)}")
print(f"Keys with >=1 reference doc: {sum(1 for e in enrichments.values() if len(e['reference_documents']) > 0)}")
